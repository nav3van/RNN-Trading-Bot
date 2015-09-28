add_library (sqlite3 
  shell.c
  sqlite3.c
  sqlite3.h
  sqlite3ext.h)

install (TARGETS sqlite3 DESTINATION bin)
install (FILES shell.c sqlite3.c sqlite3.h sqlite3ext.h DESTINATION include)
