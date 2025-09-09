# SAS (Simple Assembly)

It's a compiled language written in python and compiled to native x86_64 format

**This language is not intended to follow common rules or implement all features, it's just a playground where I can make my experiments**

### Compiling code

Right bellow we have a very simple example of the syntax:

```elixir
for 0; < 5; ++ {
  print('|');
  for 0 as i; < 10; ++ {
    if i > 4 {
      print('G');
    } else {
      print('L');
    }
  }
  println('|');
}
```

> You can find some examples at [examples folder](./examples/)

So, you just call the compiler and inform the file you want to compile: `./compiler.py ./examples/program.sas -o out`

Now, you can just run your program: `./out`

### Dependencies

- `python` (I'm using 3.12.3)
- `nasm` (I'm using version 2.16.01)
- `ld` (I'm using GNU ld (GNU Binutils for Ubuntu) 2.42)
