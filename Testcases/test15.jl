function main()
f::Integer = 3
test(f)
end
function test(a::Integer)
while a<10
a = a+1
println("a")
end
end
main()
