# NexaCL plugin template

[简体中文](README.zh-CN.md) · [Developer documentation](https://docs.pcln.top/en/plugin-sdk/) · [SDK source](https://github.com/Nexa-MC/NexaCL-Plugin-SDK)

Use this repository as a template for a runnable NexaCL Wasm plugin. It supplies a
Host-rendered page, a button, a confirmed action callback, deterministic packaging
and CI. The SDK comes from a pinned public release; no private Sidecar checkout is
needed.

## Build and install

1. Install Python 3.12 and LLVM with Clang/wasm-ld. On Debian/Ubuntu install `clang`
   and `lld`. A WASI SDK Clang also works; the guest itself does not import WASI.
2. Change `id`, `version` and `title` in `plugin.config.json`. Use your own plugin ID.
3. Run:

   ```sh
   python eng/build.py --clang clang
   python eng/verify_package.py
   ```

4. In a compatible NexaCL development build, enable developer mode, open plugin
   management, select `artifacts/plugin.zip` and review the package permissions.
5. Open the plugin page and click **Run action**. Approve the Host dialog. The
   callback returns `Desktop action completed`; cancellation must not execute it.

The first build verifies/downloads the SDK bundle recorded in `sdk.lock.json`.
Later builds verify the local cache. After the first successful download, the
Wasm build can run offline with the installed compiler and intact cache.

## Files to edit

| File | Purpose |
| --- | --- |
| `plugin.config.json` | Plugin identity, version, title and permissions |
| `wasm/plugin.c` | Lifecycle, page/action registration and callback |
| `wasm/page.nxml` | Page layout and action binding |
| `sdk.lock.json` | Exact SDK release, source commit, size and digest |
| `eng/build.py` | Compiler flags, manifest and deterministic ZIP |
| `managed-contract/` | Optional C# Bootstrap contract example, excluded from ZIP |

`PLUGIN_ID` is passed to the C compiler from the validated configuration; the
same value replaces the NXML action namespace. Keep qualified IDs owned by your
plugin. Do not edit the generated package manifest or its payload hashes manually.

## Permissions and runtime

The default asks for package-file reads, UI registration, action registration/
invocation and owned task observation. It does not request account or instance
access. Add permissions only with the capabilities your feature needs, and handle
Host denial. A registered method is not a guarantee every launcher implements it.

The installable ZIP contains `plugin.json`, `plugin.wasm` and `page.nxml`.
`nexa-wasm-1` is an import-free, bounded executable profile. All Host effects use
SDK continuations; do not open a private JSON/stdout protocol. Ordinary CLR DLLs
are not accepted as the production Desktop executable profile.

To compile the optional managed contract example, install .NET 10, run
`python eng/consume_sdk.py`, then `dotnet build managed-contract -c Release`.
It illustrates the lifecycle only; it is not packaged or installed as the plugin.

## Updating and testing

Update `sdk.lock.json` from a reviewed immutable SDK release and update the managed
PackageReference version together. Read the migration and Host-support guides.
CI compiles the actual guest and managed example and verifies packaged identities.
Also test in NexaCL: permission rejection, declined confirmation, stop/reload and
unsupported optional capabilities. A successful build does not prove those behaviors.

For SDK development only, `--sdk-root /path/to/NexaCL-Plugin-SDK` uses a local
checkout's headers. Published projects should use the pinned default.

[Contributing](CONTRIBUTING.md) · [Apache-2.0](LICENSE)
