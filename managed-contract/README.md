# Managed contract example

This project illustrates Bootstrap lifecycle and capability negotiation. It is
compiled against the same pinned SDK as the Wasm example. It is not included in
the installable ZIP: ordinary CLR DLLs are not the production Desktop executable
profile. Use `wasm/` for a runnable launcher plugin.

Run `python eng/consume_sdk.py`, then `dotnet build managed-contract -c Release`.
