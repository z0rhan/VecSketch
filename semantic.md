The language has two different kinds of types: numbers (number) and shapes (shape). (The allowed identifier in the type’s BNF syntax is there to allow user-defined types in a hypothetical future extension of the language.)

Creation of shapes happens as follows (in phase 4 you are given a library that can create shapes):

(x,y) creates a point in given coordinates.

(x1,y1)-(x2,y2)-...-(xn,yn) creates a linestring that connects the given coordinates with lines.

+(x1,y1)-(x2,y2)-...-(xn,yn) creates a (filled) polygon whose perimeter is the given linestring.

Arithmetics on numbers behaves as Python does it. Use Python / (and not //) for division so that division is not rounded to an integer. Also, unconventionally +number rounds the number down to an integer (like Python floor()).

For shapes, operations behave as defined below (in phase 4 you are given a library that can do these):

shape1 + shape2 produces the union of the two shapes.

shape1 - shape2 produces the difference of the two shapes (shape2 is “cut out” of shape 1).

shape1 * shape2 produces the intersection of the two shapes.

shape1 * number produces a scaled version of the shape. (Scaling happens by multiplying every coordinate by the number.)

shape1 / number produces a rotated version of the shape. (Rotation happens by rotating the shape counterclockwise around the origin (0,0) by the given number of degrees.)

shape1 -> (x,y) produces a moved version of the shape. (The shape is moved x units to the right and y units up.)

-shape1 produces a “downgraded” version of the shape (its “boundary”), where polygons become their outline, linestrings become their points, and points remain points.

+shape1 produces a “polygonized” version of the shape, where polygons remain polygons, linestrings become polygons whose perimeter is the linestring, and points become a polygon that contain all the points.

shape1 = shape2 and shape1 /= shape2 test if shapes are (not) equal.

shape1 < shape2 tests if shape1 is covered by shape2 (i.e. the union of shape1 and shape2 is the same as shape2).

Relational operators =, /=, and < return 0 if the comparison is false and 1 if it is true. However, the if-statements etc. interpret anything not equal to 0 as true (if you don’t implement the semantic check that requires the conditions to be direct relations).

variable.attribute can be used to query properties of shapes (in phase 4 you are given a library that can do these):

f.x gets the x-coordinate of the centroid (“center of mass”) of the shape.

f.y gets the y-coordinate of the centroid (“center of mass”) of the shape.

Additionally the following attributes can be implemented (no bonus is given for implementing these):

f.xmin gets the smallest x-coordinate in the shape.

f.xmax gets the largest x-coordinate in the shape.

f.ymin gets the smallest y-coordinate in the shape.

f.ymax gets the largest y-coordinate in the shape.

Variables and scopes
Each variable or parameter can only be defined once.

A variable can only be used after it’s been defined (i.e., you cannot refer to variables that are declared later in the source code).

Scopes of variables in the language can be implemented in several ways:

You don’t have to implement scoping. I.e., it’s ok to assume that all variables are “global” regardless of where they are defined. This implies that all variables and function/procedure parameters have to have different names so that there’s no overlap.

A little more challenging alternative (which gives you extra points) is to have all variables still as global, but check that local variables and parameter names can only be used in the function/procedure body.

Final most challenging alternative is to implement scoping, i.e. global variables and local variables (or parameters) of functions/procedures can have the same name, but still refer to different variables.

Functions and procedures
Unlike with variables, the definition of a function or procedure may appear after the place where it’s first called. (I.e., you can call a function or procedure in a variable/function/procedure definition that appears before the definition of the called function/procedure.)

The syntax dictates that functions just contain a single expression that produces an rvalue, which is the return value of the function. The return type of every function is either number or shape. Recursive function calls are not allowed (and wouldn’t be useful anyway, since there’s no way to end the recursion loop…)

For procedures, their body is a sequence of statements, followed by an optional return statement. If there is no return statement, the procedure can only be called as a stand-alone statement. If there is a return statement, the procedure can only be called as the right side of an assignment.

In the function/procedure definition, formal parameters have the form name : type. The type is either number or shape.

The language does not have to support procedure recursion, i.e. it’s not required to be possible to have two calls to the same procedure to be active at the same time. This makes it unnecessary to implement dynamic activation records, etc. You are allowed to support recursion, if you want, though, which gives you extra points. (Implementing recursion requires some sort of activation records in phase 4 for local variables and parameters, which may be somewhat complicated to do).

Each parameter name is unique in the program, see the “Variables” section above for alternatives

For parameter passing, you can decide whether to use pass-by-value or pass-by-reference. (I.e., whether assigning to a formal parameter in the procedure body changes the actual parameter.)

(Since supporting recursion is not required, you can implement function and procedure return values by creating a new global variable for each function’s return value and using that to pass return values from a function.)

Statements
The print statement prints out all the print_items on a new line and prints out one space between items. Numbers are printed as a single number (like Python outputs them by default), shapes can also be printed out directly as such, the underlying Shapely library can print them adequately.

The while statement is a traditional while loop.

The if statement is a traditional conditional if statement.

For the following drawing-related statements, you are given a library in phase 4 that can do these:

The draw statement draws the given shape on the canvas, either with the given RGB color or the default Tuni color.

The clear statement clears the canvas.

The pause statement pauses the execution until the user presses the button.

The wait statement pauses the execution for the given number of seconds (which can of course be a fractional value).
