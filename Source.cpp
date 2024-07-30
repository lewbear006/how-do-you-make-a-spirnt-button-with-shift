//Step 1 Preprocessor directives.
#include <iostream>
#include <fstream>
#include <string>
#include <windows.h>
using namespace std;

//Step 2 Declare / define variables
char maparray[201][40];
int playerrow;
int playercolumn;
int futurerow;
int futurecolumn;
bool gameover = false;
char movechoice;
int k;
HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
void ShowConsoleCursor(bool showFlag);
int x;
int y;
int c;
void gotoxy(int x, int y);



void getKeyPress();
void gotoxy(int x, int y);

int main()
{
	cin.get();
	ShowConsoleCursor(false);
	ifstream Inputfile;
	Inputfile.open("map.txt");

	for (int h = 0; h < 40; h++)
	{
		for (int i = 0; i < 201; i++)
		{
			Inputfile >> maparray[i][h];
		}

	}

	//Step 4 Place the player on the map (x, y coordinates)
	srand(time(NULL));
	playerrow = x = rand() % 38 + 2;
	playercolumn = y = rand() % 195 + 3;
	maparray[playercolumn][playerrow] = char(2);
	system("cls");

	//Step 6 Showmap

	for (int h = 0; h < 40; h++)
	{

		for (int i = 0; i < 201; i++)
		{
			if (maparray[i][h] == '#')
			{
				SetConsoleTextAttribute(hConsole, 68);
			}
			if (maparray[i][h] == '.')
			{

				SetConsoleTextAttribute(hConsole, 61);
			}
			if (maparray[i][h] == ',')
			{
				SetConsoleTextAttribute(hConsole, 0);
			}
			cout << maparray[i][h];

		}
		SetConsoleTextAttribute(hConsole, 0);
		cout << endl;

	}

	while (gameover == false)
	{
		ShowConsoleCursor(false);
		futurerow = playerrow;
		futurecolumn = playercolumn;
		getKeyPress();

		//Step 9 Recalculate position
		if (maparray[futurecolumn][futurerow] == '.')
		{
			gotoxy(playercolumn, playerrow);
			maparray[playercolumn][playerrow] = '.';
			SetConsoleTextAttribute(hConsole, 61);
			cout << '.';

			playerrow = futurerow;
			playercolumn = futurecolumn;

			gotoxy(playercolumn, playerrow);
			maparray[playercolumn][playerrow] = char(2);
			SetConsoleTextAttribute(hConsole, 61);
			cout << char(2);
			Sleep(200);
		}
	}
}





void getKeyPress()
{
	if (GetAsyncKeyState(VK_SHIFT && 0x57))
	{
		Sleep(0);
		futurerow = playerrow - 1;
	}
	else if (GetAsyncKeyState(VK_SHIFT && 0x41))
	{
		Sleep(0);
		futurecolumn = playercolumn - 1;

	}
	else if (GetAsyncKeyState(VK_SHIFT))
	{
		Sleep(0);
		futurecolumn = playercolumn - 1;

	}
	else if (GetAsyncKeyState(VK_SHIFT && 0x44))
	{
		Sleep(0);
		futurecolumn = playercolumn + 1;
	}
	else if (GetAsyncKeyState(VK_SHIFT && 0x53))
	{
		Sleep(0);
		futurerow = playerrow + 1;
	}

	else if (GetAsyncKeyState(VK_UP))
	{
		Sleep(500);
		futurerow = playerrow - 1;
	}
	else if (GetAsyncKeyState(VK_LEFT))
	{
		Sleep(500);
		futurecolumn = playercolumn - 1;
	}
	else if (GetAsyncKeyState(VK_RIGHT))
	{
		Sleep(500);
		futurecolumn = playercolumn + 1;
	}
	else if (GetAsyncKeyState(VK_DOWN))
	{
		Sleep(500);
		futurerow = playerrow + 1;

	}
	else if (GetAsyncKeyState(0x57))
	{
		Sleep(500);
		futurerow = playerrow - 1;
	}
	else if (GetAsyncKeyState(0x41))
	{
		Sleep(500);
		futurecolumn = playercolumn - 1;
	}
	else if (GetAsyncKeyState(0x44))
	{
		Sleep(500);
		futurecolumn = playercolumn + 1;
	}
	else if (GetAsyncKeyState(0x53))
	{
		Sleep(500);
		futurerow = playerrow + 1;
	}


}



void gotoxy(int x, int y)
{
	COORD coord;
	coord.X = x;
	coord.Y = y;
	SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
}



void ShowConsoleCursor(bool showFlag)
{
	HANDLE out = GetStdHandle(STD_OUTPUT_HANDLE);
	CONSOLE_CURSOR_INFO     cursorInfo;
	GetConsoleCursorInfo(out, &cursorInfo);
	cursorInfo.bVisible = showFlag;
	SetConsoleCursorInfo(out, &cursorInfo);
}


