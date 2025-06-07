#credits- https://stackoverflow.com/a/74423780
#due to some wierd inner workings of windows, none of my(or anyone else's) high level solutions worked with system files reliably
#dude/dudess was an absolute godsend after hours of banging my head against the wall

'''
This script retrieves the list of process IDs (PIDs) that are currently using a specific file in Windows.
'''

#lemme know wtf is wrong with my og implementation while ur at it :/
#catches most but not all processes(whatsapp as an example, whatapp shouldn't even be using that dll)

#import psutil
#for pid in psutil.process_iter():
#        try:
#            for opened_file in pid.open_files():
#                if "C:\\Windows\\System32\\Windows.ApplicationModel.Store.dll" == opened_file.path:
#                    print(f'Process {pid.pid} ({pid.name()}) is using the DLL.')
#                else:
#                    print(f'Process {pid.pid} ({pid.name()}) is not using the DLL.')
#        except psutil.AccessDenied:
#            print(f'Process {pid.pid} ({pid.name()}) bad process')



import ctypes
from ctypes import wintypes


def handlecatcher(path):
    """
    Retrieves the list of process IDs (PIDs) that are currently using the specified file.
    
    :param path: The path to the file to check.
    :return: Generator[int, None, None]
    """

    # -----------------------------------------------------------------------------
    # generic strings and constants
    # -----------------------------------------------------------------------------

    ntdll = ctypes.WinDLL('ntdll')
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    NTSTATUS = wintypes.LONG

    INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
    FILE_READ_ATTRIBUTES = 0x80
    FILE_SHARE_READ = 1
    OPEN_EXISTING = 3
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

    FILE_INFORMATION_CLASS = wintypes.ULONG
    FileProcessIdsUsingFileInformation = 47

    LPSECURITY_ATTRIBUTES = wintypes.LPVOID
    ULONG_PTR = wintypes.WPARAM


    # -----------------------------------------------------------------------------
    # create handle on concerned file with dwDesiredAccess == FILE_READ_ATTRIBUTES
    # -----------------------------------------------------------------------------

    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = (
        wintypes.LPCWSTR,      # In     lpFileName
        wintypes.DWORD,        # In     dwDesiredAccess
        wintypes.DWORD,        # In     dwShareMode
        LPSECURITY_ATTRIBUTES,  # In_opt lpSecurityAttributes
        wintypes.DWORD,        # In     dwCreationDisposition
        wintypes.DWORD,        # In     dwFlagsAndAttributes
        wintypes.HANDLE)       # In_opt hTemplateFile
    hFile = kernel32.CreateFileW(
        path, FILE_READ_ATTRIBUTES, FILE_SHARE_READ, None, OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS, None)
    if hFile == INVALID_HANDLE_VALUE:
        raise ctypes.WinError(ctypes.get_last_error())


    # -----------------------------------------------------------------------------
    # prepare data types for system call
    # -----------------------------------------------------------------------------

    class IO_STATUS_BLOCK(ctypes.Structure):
        class _STATUS(ctypes.Union):
            _fields_ = (('Status', NTSTATUS),
                        ('Pointer', wintypes.LPVOID))
        _anonymous_ = '_Status',
        _fields_ = (('_Status', _STATUS),
                    ('Information', ULONG_PTR))


    iosb = IO_STATUS_BLOCK()


    class FILE_PROCESS_IDS_USING_FILE_INFORMATION(ctypes.Structure):
        _fields_ = (('NumberOfProcessIdsInList', wintypes.LARGE_INTEGER),
                    ('ProcessIdList', wintypes.LARGE_INTEGER * 64))


    info = FILE_PROCESS_IDS_USING_FILE_INFORMATION()

    PIO_STATUS_BLOCK = ctypes.POINTER(IO_STATUS_BLOCK)
    ntdll.NtQueryInformationFile.restype = NTSTATUS
    ntdll.NtQueryInformationFile.argtypes = (
        wintypes.HANDLE,        # In  FileHandle
        PIO_STATUS_BLOCK,       # Out IoStatusBlock
        wintypes.LPVOID,        # Out FileInformation
        wintypes.ULONG,         # In  Length
        FILE_INFORMATION_CLASS)  # In  FileInformationClass

    # -----------------------------------------------------------------------------
    # system call to retrieve list of PIDs currently using the file
    # -----------------------------------------------------------------------------
    status = ntdll.NtQueryInformationFile(hFile, ctypes.byref(iosb),
                                        ctypes.byref(info),
                                        ctypes.sizeof(info),
                                        FileProcessIdsUsingFileInformation)
    pidList = info.ProcessIdList[0:info.NumberOfProcessIdsInList]
    for pid in pidList: yield pid