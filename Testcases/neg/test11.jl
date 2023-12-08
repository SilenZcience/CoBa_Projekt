# no return
function main()
    testA("5", 5)
end

function testA(a::String, b::Integer)::Bool
    println(a)
end

main()