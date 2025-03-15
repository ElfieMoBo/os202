#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <mpi.h>

#include "model.hpp"
#include "display.hpp"

using namespace std::string_literals;
using namespace std::chrono_literals;

struct ParamsType
{
    double length{10.};
    unsigned discretization{200u};
    std::array<double,2> wind{0.,0.};
    Model::LexicoIndices start{10u,10u};
    int nb_iterations{700}; //Ajout du nombre d'itérations pour la simulation
};

void analyze_arg( int nargs, char* args[], ParamsType& params )
{
    if (nargs ==0) return;
    std::string key(args[0]);
    if (key == "-l"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une valeur pour la longueur du terrain !" << std::endl;
            exit(EXIT_FAILURE);
        }
        params.length = std::stoul(args[1]);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    auto pos = key.find("--longueur=");
    if (pos < key.size())
    {
        auto subkey = std::string(key,pos+11);
        params.length = std::stoul(subkey);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-n"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une valeur pour le nombre de cases par direction pour la discrétisation du terrain !" << std::endl;
            exit(EXIT_FAILURE);
        }
        params.discretization = std::stoul(args[1]);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--number_of_cases=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+18);
        params.discretization = std::stoul(subkey);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-w"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une paire de valeurs pour la direction du vent !" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::string values =std::string(args[1]);
        params.wind[0] = std::stod(values);
        auto pos = values.find(",");
        if (pos == values.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(values, pos+1);
        params.wind[1] = std::stod(second_value);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--wind=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+7);
        params.wind[0] = std::stoul(subkey);
        auto pos = subkey.find(",");
        if (pos == subkey.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(subkey, pos+1);
        params.wind[1] = std::stod(second_value);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-s"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une paire de valeurs pour la position du foyer initial !" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::string values =std::string(args[1]);
        params.start.column = std::stod(values);
        auto pos = values.find(",");
        if (pos == values.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la position du foyer initial" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(values, pos+1);
        params.start.row = std::stod(second_value);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--start=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+8);
        params.start.column = std::stoul(subkey);
        auto pos = subkey.find(",");
        if (pos == subkey.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(subkey, pos+1);
        params.start.row = std::stod(second_value);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }
}

ParamsType parse_arguments( int nargs, char* args[] )
{
    if (nargs == 0) return {};
    if ( (std::string(args[0]) == "--help"s) || (std::string(args[0]) == "-h") )
    {
        std::cout << 
R"RAW(Usage : simulation [option(s)]
  Lance la simulation d'incendie en prenant en compte les [option(s)].
  Les options sont :
    -l, --longueur=LONGUEUR     Définit la taille LONGUEUR (réel en km) du carré représentant la carte de la végétation.
    -n, --number_of_cases=N     Nombre n de cases par direction pour la discrétisation
    -w, --wind=VX,VY            Définit le vecteur vitesse du vent (pas de vent par défaut).
    -s, --start=COL,ROW         Définit les indices I,J de la case où commence l'incendie (milieu de la carte par défaut)
)RAW";
        exit(EXIT_SUCCESS);
    }
    ParamsType params;
    analyze_arg(nargs, args, params);
    return params;
}

bool check_params(ParamsType& params)
{
    bool flag = true;
    if (params.length <= 0)
    {
        std::cerr << "[ERREUR FATALE] La longueur du terrain doit être positive et non nulle !" << std::endl;
        flag = false;
    }

    if (params.discretization <= 0)
    {
        std::cerr << "[ERREUR FATALE] Le nombre de cellules par direction doit être positive et non nulle !" << std::endl;
        flag = false;
    }

    if ( (params.start.row >= params.discretization) || (params.start.column >= params.discretization) )
    {
        std::cerr << "[ERREUR FATALE] Mauvais indices pour la position initiale du foyer" << std::endl;
        flag = false;
    }
    
    return flag;
}

void display_params(ParamsType const& params)
{
    std::cout << "Parametres définis pour la simulation : \n"
              << "\tTaille du terrain : " << params.length << std::endl 
              << "\tNombre de cellules par direction : " << params.discretization << std::endl 
              << "\tVecteur vitesse : [" << params.wind[0] << ", " << params.wind[1] << "]" << std::endl
              << "\tPosition initiale du foyer (col, ligne) : " << params.start.column << ", " << params.start.row << std::endl;
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    ParamsType params = parse_arguments(argc - 1, &argv[1]);
    if (!check_params(params)) {
        MPI_Finalize();
        return EXIT_FAILURE;
    }

    int local_height = params.discretization / size;
    int start_row = rank * local_height;
    int end_row = (rank == size - 1) ? params.discretization : (rank + 1) * local_height;

    Model model(params.length, params.discretization, params.wind, params.start);

    std::vector<std::uint8_t> local_fire_map((local_height + 2) * params.discretization, 0);
    std::vector<std::uint8_t> local_vegetation_map((local_height + 2) * params.discretization, 0);

    std::vector<std::uint8_t> fire_map, vegetation_map;
    
    if (rank == 0) {
        fire_map.resize(params.discretization * params.discretization);
        vegetation_map.resize(params.discretization * params.discretization);
    }

    Displayer* displayer = nullptr;
    if (rank == 0) {
        auto displayer = Displayer::init_instance(params.discretization, params.discretization);
        assert(displayer != nullptr);  // Vérifie que l'affichage est bien initialisé
        
        fire_map = model.fire_map();
        vegetation_map = model.vegetal_map();
    }

    
    // Distribution des données aux processus
    MPI_Scatter(fire_map.data(), local_height * params.discretization, MPI_UINT8_T,
    local_fire_map.data() + params.discretization, local_height * params.discretization, MPI_UINT8_T,
    0, MPI_COMM_WORLD);
    MPI_Scatter(vegetation_map.data(), local_height * params.discretization, MPI_UINT8_T,
    local_vegetation_map.data() + params.discretization, local_height * params.discretization, MPI_UINT8_T,
    0, MPI_COMM_WORLD);

    auto start_time = MPI_Wtime();

    for (int iter = 0; iter < params.nb_iterations; ++iter) {
        // Échange des cellules fantômes
        if (rank > 1) { //processus du dessus
            MPI_Send(local_fire_map.data() + params.discretization, params.discretization, MPI_UINT8_T, rank - 1, 0, MPI_COMM_WORLD);
            MPI_Recv(local_fire_map.data(), params.discretization, MPI_UINT8_T, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            
            MPI_Send(local_vegetation_map.data() + params.discretization, params.discretization, MPI_UINT8_T, rank - 1, 0, MPI_COMM_WORLD);
            MPI_Recv(local_vegetation_map.data(), params.discretization, MPI_UINT8_T, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }

        if (rank < size - 1) { //dessous
            MPI_Send(local_fire_map.data() + local_height * params.discretization, params.discretization, MPI_UINT8_T, rank + 1, 0, MPI_COMM_WORLD);
            MPI_Recv(local_fire_map.data() + (local_height + 1) * params.discretization, params.discretization, MPI_UINT8_T, rank + 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            
            MPI_Send(local_vegetation_map.data() + local_height * params.discretization, params.discretization, MPI_UINT8_T, rank + 1, 0, MPI_COMM_WORLD);
            MPI_Recv(local_vegetation_map.data() + (local_height + 1) * params.discretization, params.discretization, MPI_UINT8_T, rank + 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }

        if (rank>0) {
            model.update();
        }

        // Récolte des données
        MPI_Gather(local_fire_map.data() + params.discretization, local_height * params.discretization, MPI_UINT8_T,
                   fire_map.data(), local_height * params.discretization, MPI_UINT8_T, 0, MPI_COMM_WORLD);
        MPI_Gather(local_vegetation_map.data() + params.discretization, local_height * params.discretization, MPI_UINT8_T,
                   vegetation_map.data(), local_height * params.discretization, MPI_UINT8_T, 0, MPI_COMM_WORLD);

        // Vérification avant d'afficher
        if (rank == 0 && displayer != nullptr) {
            if (iter % 100 == 0) {
                std::cout << "Itération : " << iter << std::endl;
                displayer->update(vegetation_map, fire_map);
            }
        }
    }

    auto end_time = MPI_Wtime();
    double total_time = end_time - start_time;

    if (rank == 0) {
        std::cout << "Temps total : " << total_time << " s" << std::endl;
        std::cout << "Temps moyen par itération : " << total_time / params.nb_iterations << " s" << std::endl;
    }

    MPI_Finalize();
    return 0;
}