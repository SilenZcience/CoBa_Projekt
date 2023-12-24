

function main()
    a::Integer = 1
    b::Integer = 2
    c::Integer = 3
    d::Integer = 4
    e::Integer = 5
    f::Integer = 6
    while true
        a = b + c
        d = -a
        e = d+f
        if true
            f = 2*e
            println(a)
        else
            b = d+e
            e = e-1
            println(b)
        end
        b = f+c
    end
    println(b)
    return
end

main()
