#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
#include <fstream>
#include <string>
#include <sstream>

class Board {
public:
    unsigned long long player, opponent;
    
    Board() : player(0), opponent(0) {}
    Board(unsigned long long p, unsigned long long o) : player(p), opponent(o) {}
    
    void swap_players() {
        unsigned long long tmp = player;
        player = opponent;
        opponent = tmp;
    }
};

// Function declarations
int search(Board board);
unsigned long long get_moves(const Board& board);
std::vector<Board> get_next_boards(const Board& board);
int count_bits(unsigned long long x);
unsigned long long get_some_moves(unsigned long long P, unsigned long long mask, int dir);
unsigned long long flip_direction(unsigned long long P, unsigned long long O, unsigned long long move_bit, int dir);
Board make_move(const Board& board, int square);
bool is_game_over(const Board& board);
int final_score(const Board& board);

// Count bits in a bitboard
int count_bits(unsigned long long x) {
    int count = 0;
    while (x) {
        count += x & 1;
        x >>= 1;
    }
    return count;
}

// Get moves in a specific direction
unsigned long long get_some_moves(unsigned long long P, unsigned long long mask, int dir) {
    unsigned long long flip;
    flip = (((P << dir) | (P >> dir)) & mask);
    flip |= (((flip << dir) | (flip >> dir)) & mask);
    flip |= (((flip << dir) | (flip >> dir)) & mask);
    flip |= (((flip << dir) | (flip >> dir)) & mask);
    flip |= (((flip << dir) | (flip >> dir)) & mask);
    flip |= (((flip << dir) | (flip >> dir)) & mask);
    return (flip << dir) | (flip >> dir);
}

// Get all legal moves for the current player
unsigned long long get_moves(const Board& board) {
    const unsigned long long P = board.player;
    const unsigned long long O = board.opponent;
    const unsigned long long mask = O & 0x7E7E7E7E7E7E7E7EULL;
    
    return (get_some_moves(P, mask, 1)    // horizontal
            | get_some_moves(P, O, 8)     // vertical  
            | get_some_moves(P, mask, 7)  // diagonal /
            | get_some_moves(P, mask, 9)) // diagonal
            & ~(P | O); // mask with empties
}

// Helper function to compute flips in one direction
unsigned long long flip_direction(unsigned long long P, unsigned long long O, unsigned long long move_bit, int dir) {
    unsigned long long flipped = 0;
    unsigned long long pos = move_bit;
    
    // Keep moving in the direction
    while (true) {
        // Move position in the specified direction
        if (dir == 1) {
            pos = (pos << 1) & 0xFEFEFEFEFEFEFEFEULL; // horizontal right, no wrap
        } else if (dir == -1) {
            pos = (pos >> 1) & 0x7F7F7F7F7F7F7F7FULL; // horizontal left, no wrap
        } else if (dir == 8) {
            pos = pos << 8; // vertical up
        } else if (dir == -8) {
            pos = pos >> 8; // vertical down
        } else if (dir == 9) {
            pos = (pos << 9) & 0xFEFEFEFEFEFEFEFEULL; // diagonal up-right, no wrap
        } else if (dir == -9) {
            pos = (pos >> 9) & 0x7F7F7F7F7F7F7F7FULL; // diagonal down-left, no wrap
        } else if (dir == 7) {
            pos = (pos << 7) & 0x7F7F7F7F7F7F7F7FULL; // diagonal up-left, no wrap
        } else if (dir == -7) {
            pos = (pos >> 7) & 0xFEFEFEFEFEFEFEFEULL; // diagonal down-right, no wrap
        }
        
        if (!pos) break; // Off the board
        
        if (pos & O) {
            flipped |= pos; // Opponent piece to flip
        } else if (pos & P) {
            return flipped; // Found our piece, valid flip sequence
        } else {
            break; // Empty square, invalid flip sequence
        }
    }
    
    return 0; // No valid flip sequence
}

// Make a move and return the new board state
Board make_move(const Board& board, int square) {
    Board new_board = board;
    unsigned long long move_bit = 1ULL << square;
    
    // Calculate all flipped pieces
    unsigned long long flipped = 0;
    const unsigned long long P = board.player;
    const unsigned long long O = board.opponent;
    
    // Check all 8 directions
    int directions[8] = {1, -1, 8, -8, 9, -9, 7, -7};
    
    for (int dir : directions) {
        flipped |= flip_direction(P, O, move_bit, dir);
    }
    
    // Apply the move
    new_board.player ^= (flipped | move_bit);
    new_board.opponent ^= flipped;
    new_board.swap_players();
    
    return new_board;
}

// Check if the game is over (no moves for either player)
bool is_game_over(const Board& board) {
    if (get_moves(board) != 0) return false;
    
    Board swapped = board;
    swapped.swap_players();
    return get_moves(swapped) == 0;
}

// Calculate final score (from current player's perspective)
int final_score(const Board& board) {
    int player_discs = count_bits(board.player);
    int opponent_discs = count_bits(board.opponent);
    int empties = 64 - player_discs - opponent_discs;
    
    int score = player_discs - opponent_discs;
    
    // Add remaining empties to the winner
    if (score < 0) score -= empties;
    else if (score > 0) score += empties;
    
    return score;
}

// Get all possible next board states
std::vector<Board> get_next_boards(const Board& board) {
    std::vector<Board> next_boards;
    unsigned long long moves = get_moves(board);
    
    for (int square = 0; square < 64; square++) {
        if (moves & (1ULL << square)) {
            next_boards.push_back(make_move(board, square));
        }
    }
    
    // If no moves available, pass (swap players)
    if (next_boards.empty()) {
        Board passed = board;
        passed.swap_players();
        next_boards.push_back(passed);
    }
    
    return next_boards;
}

// Full-width minimax search
int search(Board board) {
    // Check if game is over
    if (is_game_over(board)) {
        return final_score(board);
    }
    
    // Get possible moves
    unsigned long long moves = get_moves(board);
    
    // If no moves, pass and search from opponent's perspective
    if (moves == 0) {
        board.swap_players();
        return -search(board);
    }
    
    int best_score = INT_MIN;
    
    // Try all legal moves
    for (int square = 0; square < 64; square++) {
        if (moves & (1ULL << square)) {
            Board new_board = make_move(board, square);
            int score = -search(new_board);
            best_score = std::max(best_score, score);
        }
    }
    
    return best_score;
}

Board obf_to_bitboards(const std::string& obf) {
    Board board;
    board.player = 0;
    board.opponent = 0;
    
    // Check if the string has the correct format: 64 chars + space + player + semicolon
    if (obf.length() < 67 || obf[64] != ' ' || obf[66] != ';') {
        std::cerr << "Invalid OBF format: " << obf << std::endl;
        return board;
    }
    
    char current_player = obf[65]; // X or O
    
    // Parse the 64-character board representation
    for (int i = 0; i < 64; i++) {
        char c = obf[i];
        if (c == current_player) {
            board.player |= (1ULL << i);
        } else if (c != '-') {
            board.opponent |= (1ULL << i);
        }
    }
    
    return board;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <obf_file_path>" << std::endl;
        std::cerr << "Example: " << argv[0] << " ../data/5_100k_20240510/obf" << std::endl;
        return 1;
    }
    
    std::string obf_file_path = argv[1];
    std::ifstream file(obf_file_path);
    
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << obf_file_path << std::endl;
        return 1;
    }
    
    std::string line;
    int game_count = 0;
    
    std::cout << "Processing OBF file: " << obf_file_path << std::endl;
    std::cout << "Game#\tPlayer_Discs\tOpponent_Discs\tEmpty\tFinal_Score" << std::endl;
    std::cout.flush(); // Ensure headers appear immediately
    
    while (std::getline(file, line)) {
        game_count++;
        
        // Skip empty lines
        if (line.empty()) {
            continue;
        }
        
        // Parse the OBF line into a board
        Board board = obf_to_bitboards(line);
        
        // Skip invalid boards (both player and opponent are 0)
        if (board.player == 0 && board.opponent == 0) {
            std::cerr << "Skipping invalid board at game " << game_count << std::endl;
            continue;
        }
        
        int player_discs = count_bits(board.player);
        int opponent_discs = count_bits(board.opponent);
        int empty_squares = 64 - player_discs - opponent_discs;
        
        // Calculate the final score with optimal play
        int final_score_result = search(board);
        
        std::cout << game_count << "\t" << player_discs << "\t\t" << opponent_discs 
                  << "\t\t" << empty_squares << "\t" << final_score_result << std::endl;
        std::cout.flush(); // Force output to appear immediately
        
        // Show progress every 1000 games
        if (game_count % 1000 == 0) {
            std::cerr << "Progress: Processed " << game_count << " games..." << std::endl;
            std::cerr.flush();
        }
    }
    
    file.close();
    std::cout << "\nProcessed " << game_count << " games." << std::endl;
    
    return 0;
}
