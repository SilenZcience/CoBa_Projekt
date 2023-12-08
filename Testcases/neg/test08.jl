# wrong argument types (would work in Julia, but here Boolean != Integer)
function main()
    test("5", true)
end

function test(a::String, b::Integer)
    println(a)
    println(b)
end

main()