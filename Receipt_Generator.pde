// Helena Sieh
// Date: 9/4/22 - 9/6/22
// Period: 5
// 1-10 Mini-Lab: Receipt Generator

float totalSum = 0; // sets totalSum equal to 0

// array called prices that has a list of 5 prices last purchased
float[] cart = {15.81, 8.99, 7.99, 20.99, 5.49};

// variable called totalSum that adds all the values of the array
// first price in array = 0, second = 1, third = 2, fourth = 3, fifth = 4 

println("    COSTCO");
println(" ===== WHOLESALE");

// prints the array in seperate lines:
println("-----------------------");
println("Here is your receipt:");
println("=======================");
println("Street Tacos: $" + cart[0]);
println("Eggplant: $" + cart[1]);
println("Biscoff: $" + cart[2]);
println("KS Meatballs: $" + cart[3]);
println("Milk: $" + cart[4]);
  
for (int i = 0; i < 5; i++)
{
  totalSum = totalSum + cart[i];
}

println("-----------------------");
// prints the value that is stored inside of the variable called totalSum
println("TOTAL: $" + nf(totalSum, 2,2)); // rounds the number to the hundredth
println("TAX: $2.39");
print("SUBTOTAL: $61.64");
