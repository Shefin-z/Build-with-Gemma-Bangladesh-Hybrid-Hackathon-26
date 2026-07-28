# Hogwarts Magician vs Muggle Identification via Recursion

# Problem Statement: Hogwarts Magician or Muggle?

Welcome to the magical world of Hogwarts. For centuries magicians have lived here peacefully. Recently, however, they have faced a problem: some muggles are entering Hogwarts and are mistakenly treated as magicians.

Every person in Hogwarts is identified by a positive integer. If the sum of the digits in even positions is odd, the person is considered a magician; otherwise, they are a muggle. (For example: 1324; Here 3+4 = 7, odd number; therefore, it is a magician!)

Write a recursive function (a magic spell that calls itself) that determines whether a given ID number belongs to a magician or a muggle.

### Sample Data

| Sample Input | Sample Output |
| :--- | :--- |
| 1324 | Magician |
| 245 | Muggle |

*[You can assume that the input numbers will have at least 2 digits and the leftmost digit is in position 1.]*

## সহজ বাংলা

এই সমস্যাটিতে একটি দেওয়া আইডি (ID) নম্বরের ওপর ভিত্তি করে নির্ধারণ করতে হবে ব্যক্তিটি 'Magician' নাকি 'Muggle'।

**শর্ত ও নিয়ম:**
১. নম্বরের বামদিক থেকে অবস্থান গণনা শুরু হবে (বামতম ডিজিটের অবস্থান ১)।
২. জোড় অবস্থানে (Even position: যেমন ২য়, ৪র্থ, ৬ষ্ঠ...) থাকা ডিজিটগুলোকে যোগ করতে হবে।
৩. যদি জোড় অবস্থানের ডিজিটগুলোর যোগফল একটি **বিজোড় সংখ্যা (Odd number)** হয়, তবে সে একজন **Magician**।
৪. অন্যথায় (যোগফল জোড় হলে), সে একজন **Muggle**।

**কাজ:**
একটি রিকার্সিভ ফাংশন (Recursive function) লিখতে হবে যা ডিজিটগুলোর জোড় অবস্থানের যোগফল বের করে পরীক্ষা করবে সংখ্যাটি Magician নাকি Muggle।

## Key Terms

- **Recursive Function** — এমন একটি ফাংশন যা কোনো সমস্যা সমাধানের জন্য নিজেকে বারবার কল করে।

- **Even Position** — সংখ্যার বাম দিক থেকে ২য়, ৪র্থ, ৬ষ্ঠ ইত্যাদি জোড় অবস্থান।

- **Magician** — যার আইডি নম্বরের জোড় অবস্থানের ডিজিটগুলোর যোগফল একটি বিজোড় সংখ্যা।

- **Muggle** — যার আইডি নম্বরের জোড় অবস্থানের ডিজিটগুলোর যোগফল একটি জোড় সংখ্যা।

## Code Snippets

### Recursive Solution in C++
```cpp
#include <iostream>
#include <string>
using namespace std;

// Helper recursive function to sum digits at even positions
int sumEvenPositions(string id, int pos) {
    if (pos > id.length()) {
        return 0;
    }
    int currentDigit = id[pos - 1] - '0';
    if (pos % 2 == 0) {
        return currentDigit + sumEvenPositions(id, pos + 1);
    }
    return sumEvenPositions(id, pos + 1);
}

string checkMagicianOrMuggle(string id) {
    int sum = sumEvenPositions(id, 1);
    if (sum % 2 != 0) {
        return "Magician";
    } else {
        return "Muggle";
    }
}

int main() {
    cout << checkMagicianOrMuggle("1324") << endl; // Output: Magician
    cout << checkMagicianOrMuggle("245") << endl;  // Output: Muggle
    return 0;
}
```

## Flashcards

- **Q:** Hogwarts-এর নিয়ম অনুযায়ী কখন একজন ব্যক্তি Magician হিসেবে গণ্য হবেন?
  **A:** যখন তার ID নম্বরের জোড় অবস্থানের ডিজিটগুলোর যোগফল বিজোড় (odd) হবে।

- **Q:** ID 1324 কেন Magician নির্দেশ করে?
  **A:** জোড় অবস্থান (2nd ও 4th)-এর ডিজিট হল 3 এবং 4। যোগফল 3 + 4 = 7 (বিজোড়)।

- **Q:** ID 245 কেন Muggle নির্দেশ করে?
  **A:** জোড় অবস্থান (2nd)-এর ডিজিট হল 4। যোগফল = 4 (জোড়)।

- **Q:** সমস্যাটিতে অবস্থান (position) গণনা কীভাবে শুরু করতে বলা হয়েছে?
  **A:** বামতম digit থেকে অবস্থান 1 ধরে গণনা শুরু করতে হবে।

- **Q:** রিকার্সিভ ফাংশন (Recursive function) বলতে কী বোঝায়?
  **A:** একটি ফাংশন যা নিজের কার্যসম্পাদনের জন্য নিজেকেই পুনঃপুনঃ কল করে।

## Quiz

- ID নম্বর '1324'-এর জোড় অবস্থানের ডিজিটগুলোর যোগফল কত?
  উত্তর: 7

- যদি কোনো ID নম্বরের জোড় অবস্থানের ডিজিটগুলোর যোগফল 8 হয়, তবে সে কী?
  উত্তর: Muggle

- ID নম্বর '54321'-এর জোড় অবস্থানে কোন কোন ডিজিট আছে?
  উত্তর: 4, 2

- ID '8765'-এর ক্ষেত্রে ফলাফল কী হবে? (জোড় স্থান: 7, 5 -> যোগফল = 12)
  উত্তর: Muggle