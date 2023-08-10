// Helena Sieh
// Date: 10/13/22 - 10/20/22
// Period: 5
// Quarter 1 Project


// importing sound library
import processing.sound.*;
SoundFile file;

// timer variables:
Boolean timerStart = false;
int timeLimit = 900;
int timer;

// movement of the green circles
int shapeXMovement = 0;
int shapeXMovement1 = 400;
int e;

/* ARRAY */
// array containing the top cities
String[] cities = { "Paris", "Berlin", "Tokyo", "Athens", "Florence", "Mecca", "Orlando", "Rome", "Dubai", "Bangkok", "Singapore", "London", "Madrid", "Moscow", "Barcelona", "Vienna", "Seattle", "Venice", "Beijing", "Milan", "Boston", "Lisbon", "Dallas", "Taipei", "Honolulu", "Manila"};
// chooses a random city from the array
int generator = int(random(cities.length));
// counts the number of letters of the randomly picked city
int number = cities[generator].length();
Boolean once = false;
String chosen_city = cities[generator];
String encrypted_city;

// Variables for user input
String typing = "";
// Variable to store saved text when return is hit
String saved = "";
String answer = "";


// variable that prints '_' instead of the number of letters in the city
void blank() {
  println("Encryption Format: ");
  // for loop that prints '_' instead of the number of letters in the city
  for (int i = 0; i < number; i++)
  {
    print( "___", " ");
    background(0);
    fill(0, 180, 0);
    text("___", 200, 230);
  }
}


// function that contains a countdown timer that counts down from 900 seconds
void timer() {
  // timer will start when it is true
  Boolean timerStart = true;
  int milliSeconds = millis()/1000;
  timer = timeLimit - milliSeconds;

  // when to start the timer:
  if (timerStart == true) {
    fill(0, 100, 0);
    textSize(30);
    text("Timer: "  + timer, 140, 380);
  }
  // if timer is 0, then the game is over
  if (timer < 0) {
    timer = 0;
    fill(0, 180, 0);
    background(0);
    text("Time's Up!", 130, 200);

    //System.exit(0);
  }
}


void setup() {

  // plays the sound file
  file = new SoundFile(this, "Intro X.wav");
  file.play();
  // prints a random city from the array
  println(cities[generator]);
  // calls the function blank()
  blank();

  // setting up canvas and background
  size(400, 400);
  background(0);

  // sets cursor
  cursor(HAND);
  // sets text size
  textSize(20);
  fill(0, 180, 0);
  //prints in the canvas
  text("Welcome to the Decipher Game!", 60, 150);
  text("To continue, press space", 100, 180);
}

void draw() { 
  
  // if the space key is pressed, display the text below
  if (key == ' ' || key == ' ')
  {
    background(0);
    fill(0,200,0);
    textSize(15);
    text("Type the city that is shown in the console. Hit enter to save. \n Press the mouse to see the encrypted city. \n Look at the console to see the encryption process! ", 10, 40);
    text("Press the right arrow to continue!", 90,180);
  }

  // opening up a circle door
  if (keyCode == RIGHT)
  {
    
    background(0);
    cursor(CROSS);
    // starts the countdown timer
    timer();
    
    fill(0,200,0);
    textSize(20);
    text("Press mouse when done.", 50,80);
    text("Input City: ",25,190);
    /*fill(0,200,0);
    text("Input: " + typing,25,190);
    text("Saved text: " + saved,25,230);
    saved();*/
    
    
    // circles that open up the postcard
    /*fill(0, 35, 0);
    ellipse(shapeXMovement1, 200, 350, 350);
    // draw a circle
    ellipse(shapeXMovement, 200, 350, 350);
    shapeXMovement = shapeXMovement + 3; // make the new value of shapeWidth to what it is now and add the length by five every time
    shapeXMovement1 = shapeXMovement1 - 3;*/
    
      // fills color of letters
   /* fill(0,200,0);
    text("Input: " + typing,25,190);
    text("Saved text: " + saved,25,230);
    print("IP done");*/
    /*if (key == '\n') 
    {
    saved = typing;
    answer = saved;
    //print(saved);
    }*/
    //saved(); // calls the function called saved
  }
  
  
  // opens doors
    if (keyCode == UP)
  {
    fill(0,200,0);
    text("See you there!", 150,200);
    // circles that open up the postcard
    fill(0, 35, 0);
    ellipse(shapeXMovement1, 200, 350, 350);
    // draw a circle
    ellipse(shapeXMovement, 200, 350, 350);
    shapeXMovement = shapeXMovement + 3; // make the new value of shapeWidth to what it is now and add the length by five every time
    shapeXMovement1 = shapeXMovement1 - 3;
  }
}


void keyPressed() 
{
  // If the return key is pressed, save the String
  if (key >= 'A' && key <= 'z'){
      // each letter that is typed by the user is added to the end of typing
      typing = typing + key;
      saved = typing;
      answer = saved;
      fill(0,200,0);
    text("Input City: " + typing,25,190);
    text("Saved text: " + saved,25,230);
    print("IP done");
    print("KP done");
  }
}

// saves user input
/*void saved(){   
  if (key == '\n') 
  {
    saved = typing;
    answer = saved;
    //print(saved);
    }    
  }*/   

// when mouse is pressed, it encrypts every letter the user types using the shift number
void mousePressed(){
  print("starting MP");
  float randomshift = random(25); // chooses a random cyphershift number
  int cyphershift = int(randomshift)+1; // converts float to integer and adding +1 to avoid a "zero" cyphershift
  StringBuffer encrypted_city = new StringBuffer(); //// REFERENCE used to help create cypher: https://www.geeksforgeeks.org/caesar-cipher-in-cryptography/?ref=gcse
  println("The shift number is:", cyphershift);
  
  // encodes each character that the user types in using the shift number
  for (int i=0; i < answer.length(); i++)
      {
        print("Answer Length = " + answer.length());
        //  char ch = (char)(((int)c1.charAt(i) + cyphershift - 97) % 26 + 97); // original line from reference
        char ch = (char)(((int)answer.charAt(i) + cyphershift)% 26 + 97);  //// this line modified from above - something was weird with the -97
        println(" Unencrypted letter ",answer.charAt(i), "--"); // prints each letter unshifted
        println(" Encrypted letter " , ch , " -- "); // prints each letter that is shifted
        encrypted_city.append(ch); //// this line from reference
      }
      fill(0,200,0);
      textSize(30);
      background(0);
      textSize(20);
      text(">>>> Encrypted City: " + encrypted_city, 50,200);
      println("Whole Encrypted City:" + encrypted_city + "\n\n");
      text("Press the up arrow to continue.", 50,350);
}


void door(){
  if (key == UP)
  {
    // circles that open up the postcard
    fill(0, 35, 0);
    ellipse(shapeXMovement1, 200, 350, 350);
    // draw a circle
    ellipse(shapeXMovement, 200, 350, 350);
    shapeXMovement = shapeXMovement + 3; // make the new value of shapeWidth to what it is now and add the length by five every time
    shapeXMovement1 = shapeXMovement1 - 3;
  }
}





         
