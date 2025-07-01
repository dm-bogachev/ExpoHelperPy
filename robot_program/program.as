.INTER_PANEL_D
0,14,"tcp.ip","IP:","",10,9,0
1,8,"tcp.port","Port:","",10,9,5,1,0
6,10,"Execute ","autostart","","",10,4,9,1,"PCEXEC autostart.pc",0
7,8,"speed1","SPEED 1","",10,9,4,2,0
8,8,"speed2","SPEED 2","",10,9,4,2,0
9,8,"speedmm","SPEED MM","",10,9,4,2,0
13,10,"Abort","autostart","","",10,4,9,2,"PCABORT",0
21,8,"tyterm","Terminal","",10,15,2,1,0
.END
.INTER_PANEL_TITLE
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
.END
.INTER_PANEL_COLOR_D
182,3,224,244,28,159,252,255,251,255,0,31,2,241,52,219,
.END
.PROGRAM motion ()
  CALL pg100
  BREAK
  .$data[1] = "STOP\n"
  CALL tcp.send.pc (.$data[], 1)
.END
.PROGRAM pg100 ()
  TWAIT 1
.END
.PROGRAM service ()
  TWAIT 1
.END
.PROGRAM gohome ()
  TWAIT 1
.END
.PROGRAM tcp.client.pc ()
  DO
    ; Checking for active sockets and closing them
    PRINT tyterm: "Checking for active sockets and closing them"
    TCP_STATUS .number, .ports[0], .sockets[0], .errors[0], .suberrors[0], .$ips[0]
    IF .number > 0 THEN
      FOR .i = 0 TO .number - 1
        IF .sockets[.i] <> 0 THEN
          PRINT tyterm: "Closing socket with id: ", .sockets[.i]
          TCP_CLOSE .status, .sockets[.i]
        END
      END
    END
    ;
    ; Get IP from string
    $tcp.ip.copy = $tcp.ip
    FOR .i = 1 TO 4
      .$ip = $DECODE ($tcp.ip.copy, ".", 0)
      ip[.i] = VAL (.$ip)
      IF .i < 4 THEN
        .$ip = $DECODE ($tcp.ip.copy, ".", 1)
      END
    END
    ;
    ; Connect to server
    PRINT tyterm: "Connecting to server with ip: " + $tcp.ip
    TCP_CONNECT tcp.socket, tcp.port, ip[1], tcp.connect.tmo
    ;
    ; Start data processing cycle
    IF tcp.socket >= 0 THEN
      PRINT tyterm: "Connection established with socket id:", tcp.socket
      .connected = TRUE
      ;
      ; Start receiving data cycle
      tcp.error.cnt = 0
      WHILE .connected AND tcp.error.cnt <= tcp.retry.count AND tcp.abort == FALSE DO
        TCP_RECV .status, tcp.socket, .$tcp.request[1], .request.size, tcp.receive.tmo, 255
        IF .status >= 0 THEN
          IF .request.size == 0 THEN
            tcp.error.cnt = tcp.error.cnt + 1
            PRINT tyterm: "Received data with 0 length. Error count:", tcp.error.cnt
          ELSE
            ;PRINT tyterm: .$tcp.request[1]
            CALL tcp.callback.pc (.$tcp.request[], .request.size)
          END
        ELSE
          ;tcp.error.cnt = tcp.error.cnt + 1
          PRINT tyterm: "Failed to receive data with error:", .status, ". Error count:", tcp.error.cnt
        END
      END
    ELSE
      PRINT tyterm: "Connection failed with error:", tcp.socket
      IF tcp.socket > 0 THEN
        TCP_CLOSE .status, tcp.socket
      END
    END
    ;
  UNTIL tcp.abort == TRUE
  IF tcp.socket > 0 THEN
    TCP_CLOSE .status, tcp.socket
  END
  ;
.END
.PROGRAM tcp.send.pc (.$data[],.data.length)
  ;
  IF tcp.socket > 0 THEN
    TCP_SEND .status, tcp.socket, .$data[1], .data.length, tcp.send.tmo
    IF .status >= 0 THEN
      PRINT tyterm: "Sent ", .data.length, " strings"
      FOR .i = 1 TO .data.length
        IF LEN (.$data[.i]) > 127 THEN
          PRINT tyterm: /S, .i, ": "
          PRINT tyterm: /S, $LEFT (.$data[.i], 128)
          PRINT tyterm: $MID (.$data[.i], 129)
        ELSE
          PRINT tyterm: /S, .i, ": "
          PRINT tyterm: .$data[.i]
        END
      END
    ELSE
      tcp.error.cnt = tcp.error.cnt + 1
      PRINT tyterm: "Failed to send data with error:", .status, ". Error count:", tcp.error.cnt
    END
  ELSE
    PRINT tyterm: "Failed to send data. Socket is not opened"
  END
  ;
.END
.PROGRAM tcp.callback.pc (.$data[],.data.length)
  PRINT tyterm: "Received ", .data.length, " strings"
  FOR .i = 1 TO .data.length
    IF LEN (.$data[.i]) > 127 THEN
      PRINT tyterm: /S, .i, ": "
      PRINT tyterm: /S, $LEFT (.$data[.i], 128)
      PRINT tyterm: $MID (.$data[.i], 129)
    ELSE
      PRINT tyterm: /S, .i, ": "
      PRINT tyterm: .$data[.i]
    END
  END
  ;
  $type = ""
  IF INSTR (.$data[1], ",") <> 0 THEN
    $type = $DECODE (.$data[1], ",", 0)
    .$temp = $DECODE (.$data[1], ",", 1)
  ELSE
    $type = .$data[1]
  END
  ;
  SCASE $type OF
    SVALUE "START\n":
      PRINT tyterm: .$data[1]
      CALL pgexecute.pc
      RETURN
    SVALUE "SERVICE\n":
      PRINT tyterm: .$data[1]
      CALL serviceexec.pc
      RETURN
    SVALUE "HOME\n":
      PRINT tyterm: .$data[1]
      CALL serviceexec.pc
      RETURN
  END
  ;
  PRINT tyterm: "Unhandled message. Return ALIVE"
  .$data[1] = "ALIVE\n"
  CALL tcp.send.pc (.$data[], 1)
.END
.PROGRAM autostart.pc ()
  CALL initialize.pc
  CALL tcp.client.pc
.END
.PROGRAM initialize.pc ()
  IF NOT EXISTREAL ("tyterm") THEN
    tyterm = 1
  END
  IF NOT EXISTCHAR ("$tcp.ip") THEN
    $tcp.ip = "127"
  END
  IF NOT EXISTREAL ("tcp.port") THEN
    tcp.port = 9001
  END
  IF NOT EXISTREAL ("tcp.connect.tmo") THEN
    tcp.connect.tmo = 5
  END
  IF NOT EXISTREAL ("tcp.receive.tmo") THEN
    tcp.receive.tmo = 5
  END
  IF NOT EXISTREAL ("tcp.send.tmo") THEN
    tcp.send.tmo = 5
  END
  IF NOT EXISTREAL ("tcp.retry.count") THEN
    tcp.retry.count = 10
  END
  IF NOT EXISTREAL ("tcp.abort") THEN
    tcp.abort = FALSE
  END
  PRINT tyterm: "PC initialization complete"
.END
.PROGRAM errstart.pc ()
  IF ERROR == -34021 THEN
    MC ERESET
    TWAIT 0.5
    PCEXECUTE 1: tcp.client.pc
  END
  errstart.pc ON
.END
.PROGRAM pgexecute.pc ()
  .permission = TRUE
  IF SWITCH(EMERGENCY) THEN
    PRINT tyterm: "Robot is in emergency state"
    .permission = FALSE
  END
  IF NOT SWITCH(REPEAT) THEN
    PRINT tyterm: "Robot is in teach state"
    .permission = FALSE
  END
  IF SWITCH(TEACH_LOCK) THEN
    PRINT tyterm: "Teach lock is on"
    .permission = FALSE
  END
  IF SWITCH(CS) THEN
    PRINT tyterm: "Another program is running"
    .permission = FALSE
  END
  IF .permission THEN
    IF NOT SWITCH(POWER) THEN
      PRINT tyterm: "Turning on motor power"
      MC ZPOWER ON
      TWAIT 1
    END
    MC EXECUTE motion
  END
  
.END
.PROGRAM get.state.pc ()
  $state = "ROBOT_STATE;"
  $state = $state + "POWER:" + $ENCODE(/L, -SWITCH(POWER)) + ";"
  $state = $state + "REPEAT:" + $ENCODE(/L, -SWITCH(REPEAT)) + ";"
  $state = $state + "ERROR:" + $ENCODE(/L, -SWITCH(ERROR)) + ";"
  $state = $state + "CS:" + $ENCODE(/L, -SWITCH(CS)) + ";"
  $state = $state + "TEACH_LOCK:" + $ENCODE(/L, -SWITCH(TEACH_LOCK)) + ";"
  $state = $state + "EMERGENCY:" + $ENCODE(/L, -SWITCH(EMERGENCY)) + ";"
  $state = $state + "SAFETY_FENCE:" + $ENCODE(/L, -SWITCH(SAFETY_FENCE)) + ";"
  $state = $state + "HOME:" + $ENCODE(/L, -SIG(33)) + "\n"
.END
.PROGRAM serviceexec.pc ()
  .permission = TRUE
  IF SWITCH(EMERGENCY) THEN
    PRINT tyterm: "Robot is in emergency state"
    .permission = FALSE
  END
  IF NOT SWITCH(REPEAT) THEN
    PRINT tyterm: "Robot is in teach state"
    .permission = FALSE
  END
  IF SWITCH(TEACH_LOCK) THEN
    PRINT tyterm: "Teach lock is on"
    .permission = FALSE
  END
  IF SWITCH(CS) THEN
    PRINT tyterm: "Another program is running"
    .permission = FALSE
  END
  IF .permission THEN
    IF NOT SWITCH(POWER) THEN
      PRINT tyterm: "Turning on motor power"
      MC ZPOWER ON
      TWAIT 1
    END
    MC EXECUTE service
  END
  
.END
.PROGRAM homeexec.pc ()
  .permission = TRUE
  IF SWITCH(EMERGENCY) THEN
    PRINT tyterm: "Robot is in emergency state"
    .permission = FALSE
  END
  IF NOT SWITCH(REPEAT) THEN
    PRINT tyterm: "Robot is in teach state"
    .permission = FALSE
  END
  IF SWITCH(TEACH_LOCK) THEN
    PRINT tyterm: "Teach lock is on"
    .permission = FALSE
  END
  IF SWITCH(CS) THEN
    PRINT tyterm: "Another program is running"
    .permission = FALSE
  END
  IF .permission THEN
    IF NOT SWITCH(POWER) THEN
      PRINT tyterm: "Turning on motor power"
      MC ZPOWER ON
      TWAIT 1
    END
    MC EXECUTE gohome
  END
  
.END
.PROGRAM Comment___ () ; Comments for IDE. Do not use.
	; @@@ PROJECT @@@
	; @@@ PROJECTNAME @@@
	; program
	; @@@ HISTORY @@@
	; @@@ INSPECTION @@@
	; @@@ CONNECTION @@@
	; KROSET R01
	; 127.0.0.1
	; 9105
	; @@@ PROGRAM @@@
	; 0:motion:F
	; 0:pg100:F
	; 0:service:F
	; 0:gohome:F
	; Group:TCPIP:1
	; 1:tcp.client.pc:B
	; .number 
	; .ports 
	; .sockets 
	; .errors 
	; .suberrors 
	; .i 
	; .status 
	; .connected 
	; .request.size 
	; 1:tcp.send.pc:B
	; .$data[] 
	; .data.length 
	; .status 
	; .i 
	; 1:tcp.callback.pc:B
	; .$data[] 
	; .data.length 
	; .i 
	; 0:autostart.pc:B
	; 0:initialize.pc:B
	; 0:errstart.pc:B
	; 0:pgexecute.pc:B
	; .permission 
	; 0:get.state.pc:B
	; 0:serviceexec.pc:B
	; .permission 
	; 0:homeexec.pc:B
	; .permission 
	; @@@ TRANS @@@
	; @@@ JOINTS @@@
	; @@@ REALS @@@
	; @@@ STRINGS @@@
	; @@@ INTEGER @@@
	; @@@ SIGNALS @@@
	; @@@ TOOLS @@@
	; @@@ BASE @@@
	; @@@ FRAME @@@
	; @@@ BOOL @@@
	; @@@ DEFAULTS @@@
	; BASE: NULL
	; TOOL: NULL
	; @@@ WCD @@@
	; SIGNAME: sig1 sig2 sig3 sig4
	; SIGDIM: % % % %
.END
