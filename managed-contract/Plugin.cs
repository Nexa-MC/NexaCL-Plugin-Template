using Nexa.Plugin.Bootstrap.V1;
using Nexa.Plugin.Sdk.Abi100;
namespace HelloPlugin;

public sealed class Plugin : IPluginBootstrapV1
{
    public async ValueTask<AbiReply<PreInitResult>> OnPreInitialize(PreInitContext context)
    {
        var options = new InvocationOptions(Guid.NewGuid(), context.Budget, context.Cancellation);
        var draft = await context.Negotiator.GetABIContext(100, options);
        if (!draft.Success) return AbiReply<PreInitResult>.Fail(draft.Error!);
        var ready = await new Abi100Draft(draft.Value).Require("nexa.diagnostics", 1).Optional("nexa.ui", 1)
            .Make(context.Negotiator, Guid.NewGuid(), [], context.Cancellation);
        return ready.Success ? AbiReply<PreInitResult>.Ok(new(ready.Value, [], [], [], [])) : AbiReply<PreInitResult>.Fail(ready.Error!);
    }
    public ValueTask<AbiReply<Unit>> OnInitialize(ABIContext abi, StageContext stage) => Ok();
    public ValueTask<AbiReply<Unit>> OnPostInitialize(ABIContext abi, StageContext stage) => Ok();
    public async ValueTask<AbiReply<CheckupResult>> OnCheckup(ABIContext abi, StageContext stage)
    {
        using var api = abi.ForStage100(stage);
        var registrations = await api.Diagnostics.QueryRegistrations(new(Guid.NewGuid(), stage.Budget, stage.Cancellation));
        return registrations.Success
            ? AbiReply<CheckupResult>.Ok(new(CheckupStatus.Passed, [], []))
            : AbiReply<CheckupResult>.Fail(registrations.Error!);
    }
    public ValueTask<AbiReply<Unit>> OnFinalize(ABIContext abi, StageContext stage) => Ok();
    public ValueTask<AbiReply<Unit>> OnActivated(ABIContext abi, InvocationContext invocation) => Ok();
    public ValueTask<AbiReply<Unit>> OnAbort(AbortContext context) => Ok();
    public ValueTask<AbiReply<Unit>> OnStop(StopContext context) => Ok();
    private static ValueTask<AbiReply<Unit>> Ok() => ValueTask.FromResult(AbiReply<Unit>.Ok(new()));
}
