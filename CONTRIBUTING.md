# Contributing

Keep the default Wasm package runnable with only the documented permissions.
Build with the pinned SDK and verify the manifest after every source or asset
change. Keep plugin IDs synchronized through configuration, not copied literals.

Run `python eng/build.py`, `python eng/verify_package.py`, and
`dotnet build managed-contract -c Release`. Documentation belongs at
https://docs.pcln.top/en/plugin-sdk/ with source in NexaCL-Plugin-SDK.
Do not add production credentials, publisher private keys, account data or build
outputs to the template.
