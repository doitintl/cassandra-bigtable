from dl import metric as metric_dl

import argparse
import random
import threading
import time
import sys


def emit_metrics(server, cass_session, bt_session, skip_bt_insert):
    count = 0
    while True:
        count += 1
        metric = metric_dl.Metric(server)
        cass_session.insert_row(metric)
        if not skip_bt_insert:
            bt_session.insert_row(metric)
        print('Server {} emitted total {} metric'.format(server, count))
        time.sleep(random.randrange(5, 9))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--servers',
        type=int,
        help='Number of servers to simulate',
        default=1)
    parser.add_argument(
        '--cassandra_host',
        help='Cassandra endpoint',
        required=True)
    parser.add_argument(
        '--cassandra_ks',
        help='Cassandra keyspace',
        required=False,
        default='metric')
    parser.add_argument(
        '--bt_project_id',
        help='Bigtable project id',
        required=False)
    parser.add_argument(
        '--bt_instance_id',
        help='Bigtable instance id',
        required=False)
    parser.add_argument(
        '--skip_bt_insert',
        help='Skip inserting data to bigtable',
        action='store_true',
        default=False)

    args = parser.parse_args()

    if not args.skip_bt_insert:
        if not args.bt_project_id:
            print('Missing bigtable project id argument')
            sys.exit(1)
        if not args.bt_instance_id:
            print('Missing bigtable instance id argument')
            sys.exit(1)
    else:
        if args.bt_project_id or args.bt_instance_id:
            print('Bigtable arguments ignored...')

    # Cassandra connection
    cass_session = metric_dl.CassandraMetric(args.cassandra_host, args.cassandra_ks)

    # Bigtable connection
    bt_session = None
    if args.skip_bt_insert:
        bt_session = None
    else:
        bt_session = metric_dl.BigtableMetric(args.bt_project_id, args.bt_instance_id)

    num_of_servers = args.servers

    servers = [random.randrange(0, 2**32) for _ in range(num_of_servers)]
    print('bringing up {} servers...'.format(servers))
    for server in servers:
        thread = threading.Thread(target=emit_metrics, args=(server, cass_session, bt_session, args.skip_bt_insert))
        thread.start()

