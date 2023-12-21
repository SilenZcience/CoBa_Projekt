; manuell geschrieben:
.bytecode 50.0
.class public test00m
.super java/lang/Object

.method public <init>()V
   aload_0
   invokenonvirtual java/lang/Object/<init>()V
   return
.end method

.method public static x()V
    .limit locals 0
    .limit stack 10

    getstatic java/lang/System/out Ljava/io/PrintStream;
    ldc "x"
    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V

    return
.end method

.method public static main([Ljava/lang/String;)V
    .limit locals 3
    .limit stack 100

    ldc 1
    istore_0

    ldc 2
    istore_1

    ldc 0
    istore_2

    getstatic java/lang/System/out Ljava/io/PrintStream;
    iload_0
    invokevirtual java/io/PrintStream/println(I)V

    Label1:

    iload_0
    ldc 144

    if_icmpge Label2

    iload_1
    istore_2

    iload_0
    iload_1
    iadd
    istore_1

    iload_2
    istore_0

    getstatic java/lang/System/out Ljava/io/PrintStream;
    iload_0
    invokevirtual java/io/PrintStream/println(I)V

    goto Label1

    Label2:

    ; enter println
    getstatic java/lang/System/out Ljava/io/PrintStream;

    ; exit Expr
    ldc "Hello World"
    ; exit FunctionCall
    invokestatic test00m/lol(Ljava/lang/String;)D
    ; exit Println
    invokevirtual java/io/PrintStream/println(D)V


    invokestatic test00m/x()V


    ; exit Return
    return
.end method

.method public static lol(Ljava/lang/String;)D
    .limit locals 3
    .limit stack 4

    ldc 20
    i2d
    dstore_1

    ldc 5
    i2d
    dstore_1

    getstatic java/lang/System/out Ljava/io/PrintStream;
    dload_1
    invokevirtual java/io/PrintStream/println(D)V

    getstatic java/lang/System/out Ljava/io/PrintStream;
    aload_0
    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V

    dload_1
    dreturn
.end method

; Method: .method public static x(typetypetype...)type/V
; InvokeMethod: invokestatic className/x(typetypetype...)type/V
; I: Integer 32bit istore,iload,ldc,ireturn  (Boolean = 1/0)
; D: Float64 64Bit dstore,dload,ldc2_w,dreturn
; Ljava/lang/String;: String 32Bit astore,aload,ldc,areturn
; .limit locals (len(locals)+len(locals that are type Float64))
; .limit stack (amount push operations -> too much, but simple)