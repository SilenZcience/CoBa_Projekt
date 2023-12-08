# too few arguments
function main()
    test("5")
end

function test(a::String, b::Integer)
    println(a)
end

main()