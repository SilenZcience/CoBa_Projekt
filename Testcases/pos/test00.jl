
function x()
    println("x")
end

function main()
    a::Integer = 1
        b::Integer = 1
        temp::Integer = 0
    println("Fibonacci:")
        while a < 144
            temp = b
                b = a + b
                a = temp
                println(a)
        end
    println("Calling other functions:")
    println(test_function("a"))
    x()
end

function test_function(x::String)::Float64
    a::Float64 = 20/3
    a = 5
    if (5/5+5*2 > 2)
        println(a)
    end
    return a
end

main()
