function fib(n::Integer)::Integer
    if n == 0
        return 0
    else
        if n == 1
            return 1
        else
            return fib(n-1) + fib(n-2)
        end
    end
end

function gcd_recursive(a::Integer, b::Integer)::Integer
    if b == 0
        return a
    else
        return gcd_recursive(b, a % b)
    end
end

function main()

    a::Integer = 20/3
    b::Float64 = 20/3
    println(a)
    println(b)
    println(fib(7))

    println(gcd_recursive(8096,17318))
end

main()
