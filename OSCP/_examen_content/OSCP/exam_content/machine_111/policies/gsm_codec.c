void systemo(){
	 MessageBox( 0, "3c184981367094fce3ab70efc3b44583" , "philbin :)" , MB_YESNO + MB_ICONQUESTION );
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL,DWORD fdwReason,LPVOID lpvReserved){
	switch(fdwReason){
		case DLL_PROCESS_ATTACH:{
			 systemo();
			break;
		}
		case DLL_PROCESS_DETACH:{
			 systemo();
			break;
		}
		case DLL_THREAD_ATTACH:{
			 systemo();
			break;
		}
		case DLL_THREAD_DETACH:{
			 systemo();
			break;
		}
	}

	return TRUE;
}

