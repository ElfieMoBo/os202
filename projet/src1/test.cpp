#include <stdexcept>
#include <cmath>
#include <iostream>
#include <cstdint>
#include <array>
#include <vector>
#include <unordered_map>


int main(){
    std::unordered_map<char, int> dict;
    dict.insert({'a', 4});
    dict.insert({'b', 5});
    std::unordered_map<char,int>::iterator it;
    for (it = dict.begin (); it != dict.end(); it++)
    {
        std::cout << it->first << " ";
        std::cout << it-> second << '\n';
    }
    std::cout << "\n";
    auto search = dict.find('a');
    std::cout << search->second << std::endl;
}  


