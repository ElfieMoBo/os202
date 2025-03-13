#include<iostream>
#include<fstream>

int main(){
    std::ifstream sequentialOutput("sequential.txt");
    if(!sequentialOutput)
        return 1;
    std::ifstream parallelOutput("simulation.txt");
    if(!parallelOutput)
        return 1;
    
}