# one wrong return
function test()::Float64
    a::Integer = 5
    if a % 2 == 0
        return 5.5
    end
    return true
    return 6.0
end

function main()
    while false
    end
end

main()


