println('Board:');

for 0; < 12; ++ {
  print('-');
}

println('');

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

for 0; < 12; ++ {
  print('-');
}

println('');

println('Depth-1 loop');

for 10; > 0; -- {
  println('10 lines');
}

println('Nested loops:');

# the order of the functions matter. It is like C

fn displayNestedPrints() {
  println('    + First item');
  println('    + Second item. Same level');
}

fn displayFirstLevel() {
  for 0; < 2; ++ {
    println('  Second:');

    for 0; < 2; ++ {
      displayNestedPrints();
    }
  }
}

fn thatIsAnEmptyFunction() {}

for 2; != 4; ++ {
  println('First:');

  displayFirstLevel();
}

thatIsAnEmptyFunction();
