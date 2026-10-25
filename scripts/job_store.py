#!/usr/bin/env python3
"""Offline JSONL job store. Does not contact websites or submit applications."""
import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TYPES = {'daily_internship', 'summer_internship', 'campus', 'unknown'}
SYSTEM = {'key', 'first_seen', 'last_seen', 'history', 'identity_aliases'}
STATUSES = {'open', 'closed', 'expired', 'unverified', 'inaccessible'}


def timestamp(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('verified_at must contain a timezone')
    return dt


def clean_url(value):
    if not isinstance(value, str):
        raise ValueError('URL must be a string')
    parts = urlsplit(value)
    if parts.scheme not in ('https', 'http') or not parts.netloc or parts.username or parts.password:
        raise ValueError('Expected a public HTTP(S) URL without credentials')
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in {'spm', 'gclid', 'fbclid'}]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or '/',
                       urlencode(query), parts.fragment))


def prepare(record):
    if not isinstance(record, dict):
        raise ValueError('Each job must be an object')
    for field in ('company', 'title', 'url', 'verified_at'):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f'Missing or invalid {field}')
    timestamp(record['verified_at'])
    kinds = record.get('types')
    if not isinstance(kinds, list) or not kinds or any(t not in TYPES for t in kinds):
        raise ValueError('types must be a nonempty array of supported types')
    if 'unknown' in kinds and len(kinds) != 1:
        raise ValueError('unknown cannot coexist with another type')
    if record.get('status') is not None and record['status'] not in STATUSES:
        raise ValueError('Unsupported status')
    for field in ('official_company_id', 'job_id'):
        if record.get(field) is not None and (not isinstance(record[field], str) or not record[field].strip()):
            raise ValueError(f'{field} must be a nonempty string or null')
    data = {k: v for k, v in record.items() if k not in SYSTEM}
    data['url'] = clean_url(data['url'])
    if data.get('official_url'):
        data['official_url'] = clean_url(data['official_url'])
    if data.get('official_company_id') and data.get('job_id'):
        identity = json.dumps([data['official_company_id'], data['job_id']], ensure_ascii=False)
    else:
        identity = data.get('official_url') or data['url']
    data['key'] = hashlib.sha256(identity.encode()).hexdigest()[:24]
    return data


def aliases(data):
    result = {'url:' + clean_url(data['url'])}
    if data.get('official_url'):
        result.add('url:' + clean_url(data['official_url']))
    if data.get('official_company_id') and data.get('job_id'):
        result.add('id:' + json.dumps([data['official_company_id'], data['job_id']], ensure_ascii=False))
    return result


def ingest(existing, incoming):
    prepared = [prepare(r) for r in incoming]
    rows = {}
    for old in existing:
        prepare(old)
        if not isinstance(old.get('key'), str) or old['key'] in rows:
            raise ValueError('Store contains missing or duplicate keys; repair it before updating')
        if not isinstance(old.get('history'), list):
            raise ValueError('Invalid store history')
        for field in ('first_seen', 'last_seen'):
            timestamp(old[field])
        saved_aliases = old.get('identity_aliases', [])
        if not isinstance(saved_aliases, list) or any(not isinstance(v, str) for v in saved_aliases):
            raise ValueError('Invalid identity aliases')
        rows[old['key']] = dict(old)
    for data in sorted(prepared, key=lambda r: timestamp(r['verified_at'])):
        identities = aliases(data)
        matches = [k for k, r in rows.items()
                   if identities & (aliases(r) | set(r.get('identity_aliases', [])))]
        if len(matches) > 1:
            raise ValueError('Ambiguous identity matches multiple saved jobs; reconcile manually')
        key = matches[0] if matches else data['key']
        now = data['verified_at']
        old = rows.get(key)
        if old is None:
            rows[key] = dict(data, first_seen=now, last_seen=now, history=[],
                             identity_aliases=sorted(identities))
            continue
        # Preserve the original key so application records keep referring to this job.
        if timestamp(now) < timestamp(old['verified_at']):
            continue
        old_ids = (old.get('official_company_id'), old.get('job_id'))
        new_ids = (data.get('official_company_id'), data.get('job_id'))
        if all(old_ids) and all(new_ids) and old_ids != new_ids:
            raise ValueError('Conflicting official IDs for the same URL')
        changes = {k: {'before': old.get(k), 'after': v} for k, v in data.items()
                   if k not in {'key', 'verified_at'} and old.get(k) != v}
        history = list(old['history'])
        if changes:
            history.append({'at': now, 'changes': changes})
        data['key'] = key
        rows[key] = dict(old, **data, last_seen=now, history=history,
                         identity_aliases=sorted(identities | aliases(old) | set(old.get('identity_aliases', []))))
    return list(rows.values())


def read_rows(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def save(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.jobs-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            for row in rows:
                out.write(json.dumps(row, ensure_ascii=False) + '\n')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    add = sub.add_parser('ingest')
    add.add_argument('--input', type=Path, required=True)
    listing = sub.add_parser('list')
    listing.add_argument('--type', choices=sorted(TYPES))
    args = parser.parse_args()
    try:
        args.store = args.store.expanduser()
        if args.command == 'ingest':
            incoming = json.loads(args.input.read_text(encoding='utf-8'))
            if not isinstance(incoming, list):
                raise ValueError('Input must be a JSON array')
            args.store.parent.mkdir(parents=True, exist_ok=True)
            lock = args.store.with_name(args.store.name + '.lock')
            try:
                lock.mkdir()
            except FileExistsError:
                raise ValueError(f'Store is locked: {lock}. Retry after the other writer finishes; after a crash verify no writer is running before removing the lock directory.')
            try:
                rows = ingest(read_rows(args.store), incoming)
                save(args.store, rows)
            finally:
                lock.rmdir()
            print(json.dumps({'records': len(rows), 'store': str(args.store)}, ensure_ascii=False))
        else:
            for row in read_rows(args.store):
                if not args.type or args.type in row['types']:
                    print(json.dumps(row, ensure_ascii=False))
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
