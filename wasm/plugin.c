#include <nexa/abi100.h>
#ifndef PLUGIN_ID
#define PLUGIN_ID "example.plugin"
#endif
static nx_u8 input[65536], output[65536], arguments[32768];
static int step;
NX_EXPORT("nexa_alloc") nx_u32 nexa_alloc(nx_u32 size) { nx_require(size<=sizeof input); return (nx_u32)(__UINTPTR_TYPE__)input; }
NX_EXPORT("nexa_resume") nx_u64 nexa_resume(nx_u32 address,nx_u32 size) {
 nx_require(address==(nx_u32)(__UINTPTR_TYPE__)input && size<=sizeof input);
 nx_value message=nx_decode(input,size); nx_writer reply={output,0,sizeof output},args={arguments,0,sizeof arguments}; nx_call_options options={0};
 if(nx_is_string(nx_field(message,"kind"),"reply")) {
  if(!nx_reply_success(message)) {step=0;nx_handler_error(&reply,nx_reply_error(message));}
  else if(step==1) {
   nx_FileRef file;nx_require(nx_Files_OpenPackageFile_result(message,&file));
   nx_UIPage page=nx_UIPage_write(&args,nx_literal(PLUGIN_ID ":home"),file,nx_schema_Empty(&args),nx_QualifiedIdArray_write(&args,0,0));
   options.idempotency_key="page";step=2;nx_UI_RegisterPage(&reply,page,&options);
  } else if(step==2) {
   nx_stringArray strings=nx_stringArray_write(&args,0,0);
   nx_LocalizedText title=nx_LocalizedText_write(&args,nx_literal("Run sample action"),nx_NamedValueArray_write(&args,0,0));
   nx_ActionDescriptor action=nx_ActionDescriptor_write(&args,nx_literal(PLUGIN_ID ":hello"),nx_schema_Empty(&args),nx_schema_TextResult(&args),strings,strings,nx_IdempotencyMode_ReadOnly,1,0,nx_ConfirmationRequirement_UserConfirmation,nx_QualifiedIdOptional_none(&args),title,nx_ulongOptional_some(&args,1));
   options.idempotency_key="action";step=3;nx_Actions_Register(&reply,action,&options);
  } else {step=0;nx_complete(&reply,1);}
 } else if(nx_is_string(nx_field(message,"kind"),"handler")) {
  nx_require(nx_handler_id(message)==1);nx_TextResult value=nx_TextResult_write(&args,nx_literal("Desktop action completed"));nx_handler_success(&reply,value.value);
 } else if(nx_is_string(nx_field(message,"phase"),"Initialize")) {
  step=1;nx_Files_OpenPackageFile(&reply,nx_PackageFileRequest_write(&args,nx_literal("page.nxml")),&options);
 } else nx_complete(&reply,1);
 return nx_result(&reply);
}
