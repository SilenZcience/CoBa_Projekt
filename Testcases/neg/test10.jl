# no return type
function main()
    testA("5", 5)
end

function testA(a::String, b::Integer)::Bool
    println(a)
    return
end

main()