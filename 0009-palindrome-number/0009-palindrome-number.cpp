class Solution {
public:
    bool isPalindrome(int x) {
        int orignal = x;
        long long reversed = 0;

        if (x < 0)
            return false;

        while (x > 0) {
            int digit = x % 10;
            reversed = reversed * 10 + digit;
            x = x / 10;
        }

        if (reversed == orignal)
            return true;
        else
            return false;
    }
};