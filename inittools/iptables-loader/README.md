# IPTables Loader Script

This bash script loads iptables rules from the given rule file, and will only proceed to load the rule only if the given rule is not already exists. Optionally, this script can write to file regarding the rules that it loaded. This file can be used by this script to unload the rules, effectively enables iptables rules to be loaded or unloaded cleanly.

No other dependencies are required besides the `iptables` executable itself (must be accessible on this script's `PATH`).

## Usage

1. `iptables-loader.sh load (rules_file) [unload_file]`

 This form loads the rules specified in the `rules_file` and exits. Only rules that is not already existing on current iptables instance will be actually loaded. Optionally, `unload_file` can be specified. If it is specified, this script will write to that file regarding rules that this script actually loads to the local iptables instance.

2. `iptables-loader.sh unload (unload_file)`

  This form unloads (delete) the iptables rule specified inside the `unload_file` that was generated from `load` command, and then exits. This command **does not** remove the `unload_file` after it finishes.

Please note that this scripts only performs (very) minimal checks. Therefore, user is expected to ensure the correctness of the `rules_file` to avoid undefined behaviours.
  
## Rules File Format
The rule file is a simple comma separated file, with the format as follows:

`<table_name>,<insert_mode>,<chain>,<iptables_rule>`

All fields are mandatory.

- `table_name` is the iptables table name, such as `filter`, `nat`, etc. For default iptables table, use `filter`.
- `insert_mode` can be either `A` or `I`. `A` appends the given rule to the end of the given table/chain combination, whereas `I` prepends the given rule to the beginning of the given table/chain combination. Insertion in the middle of the chain is not supported.
- `chain` is the iptables chain for the given `table_name` (e.g. `POSTROUTING` and `PREROUTING` for the `nat` table). This can vary considerably depending on the choosen table, kernel version, kernel module, etc.
- `iptables_rule` is the rule that is to be added. This rule will be directly passed to the system's `iptables` utility.