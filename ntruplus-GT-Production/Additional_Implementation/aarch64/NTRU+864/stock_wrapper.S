.text
.global stock_to
.global _stock_to
_stock_to:
stock_to:
 stp x29,x30,[sp,#-80]!
 stp d8,d9,[sp,#16]
 stp d10,d11,[sp,#32]
 stp d12,d13,[sp,#48]
 stp d14,d15,[sp,#64]
 bl raw_to
 ldp d8,d9,[sp,#16]
 ldp d10,d11,[sp,#32]
 ldp d12,d13,[sp,#48]
 ldp d14,d15,[sp,#64]
 ldp x29,x30,[sp],#80
 ret
.global stock_from
.global _stock_from
_stock_from:
stock_from:
 stp x29,x30,[sp,#-80]!
 stp d8,d9,[sp,#16]
 stp d10,d11,[sp,#32]
 stp d12,d13,[sp,#48]
 stp d14,d15,[sp,#64]
 bl raw_from
 ldp d8,d9,[sp,#16]
 ldp d10,d11,[sp,#32]
 ldp d12,d13,[sp,#48]
 ldp d14,d15,[sp,#64]
 ldp x29,x30,[sp],#80
 ret
.global stock_shuffle
.global _stock_shuffle
_stock_shuffle:
stock_shuffle:
 stp x29,x30,[sp,#-80]!
 stp d8,d9,[sp,#16]
 stp d10,d11,[sp,#32]
 stp d12,d13,[sp,#48]
 stp d14,d15,[sp,#64]
 bl raw_shuffle
 ldp d8,d9,[sp,#16]
 ldp d10,d11,[sp,#32]
 ldp d12,d13,[sp,#48]
 ldp d14,d15,[sp,#64]
 ldp x29,x30,[sp],#80
 ret
.global stock_shuffle2
.global _stock_shuffle2
_stock_shuffle2:
stock_shuffle2:
 stp x29,x30,[sp,#-80]!
 stp d8,d9,[sp,#16]
 stp d10,d11,[sp,#32]
 stp d12,d13,[sp,#48]
 stp d14,d15,[sp,#64]
 bl raw_shuffle2
 ldp d8,d9,[sp,#16]
 ldp d10,d11,[sp,#32]
 ldp d12,d13,[sp,#48]
 ldp d14,d15,[sp,#64]
 ldp x29,x30,[sp],#80
 ret
