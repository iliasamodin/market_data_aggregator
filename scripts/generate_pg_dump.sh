set -euo pipefail
set -a
. "$PWD"/.env.dumps
set +a

cyan='\033[0;36m'
nc='\033[0m'

PATH_TARGET_DUMP=./dumps
current_date=$(date +%Y_%m_%d)
name="$PATH_TARGET_DUMP/dump_$current_date.sql"

declare -a tables=(
  trading.algorithm_configs
  trading.exchanges
  trading.group_algorithm_configs
  trading.groups
  trading.signal_calculation_configs
  trading.tickers
)

pg_dump_args=(
  --format=p
  --data-only
  --inserts
  --on-conflict-do-nothing
  --no-comments
  --no-sync
  --no-password
)
for table in "${tables[@]}"; do
  pg_dump_args+=(-t "$table")
done

ls -alh "$PATH_TARGET_DUMP"

pg_dump "${pg_dump_args[@]}" | grep -v "^SET transaction_timeout" > "$name"

ls -alh "$PATH_TARGET_DUMP"

printf "${cyan}--Dump is done${nc}\n"
