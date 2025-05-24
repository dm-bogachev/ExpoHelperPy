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
  JMOVE #p1
  JMOVE #p2
  JMOVE #p3
  JMOVE #p4
  JMOVE #p5
  BREAK
  ; ------------------------------
  .$data[1] = "PROGRAM COMPLETE"
  CALL tcp.send.pc (.$data[], 1)
.END
.PROGRAM calibrate ()

  LMOVE f0
  LMOVE fx
  LMOVE fy
  ;
  POINT f = FRAME(f0, fx, fy, f0)
  ;
  LMOVE f + TRANS(286, 410)
  LMOVE f + TRANS(0, 410)
  LMOVE f + TRANS(286, 0)
  LMOVE f + TRANS(0, 0)
  ;
  LMOVE f + TRANS(y, x, 20)
  LMOVE f + TRANS(183, 143.2, 20)
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
    SVALUE "START":
      PRINT tyterm: .$data[1]
      CALL pgexecute.pc
      RETURN
  END
  ;
  PRINT tyterm: "Unhandled message. Return ALIVE"
  .$data[1] = "ALIVE"
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
    tcp.port = 48569
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
	; 0:calibrate:F
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
	; .pgname 
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
	; tcp.abort 
	; @@@ DEFAULTS @@@
	; BASE: NULL
	; TOOL: NULL
	; @@@ WCD @@@
	; SIGNAME: sig1 sig2 sig3 sig4
	; SIGDIM: % % % %
.END
.JOINTS
#start 16.935207 -8.928955 -142.506897 0.432422 -46.324539 -14.192482
#pre.tare 12.028270 43.876831 -74.849274 0.000880 -61.274872 -11.075840
#pos.longs -9.564698 33.646362 -106.934273 2.620020 -60.759205 5.005275
#pos.longs.up -9.219728 29.253662 -100.866653 2.284277 -71.221619 5.233283
#machine.up 23.900537 27.906740 -115.699707 68.160065 -101.928413 29.312017
#machine 23.900537 46.515015 -113.202690 65.858208 -95.598915 14.311533
#ok 31.955280 39.942261 -109.067627 -3.841700 -33.355869 -31.666140
#ng 47.923241 29.784300 -129.056671 -6.845800 -22.939449 -44.537041
#longs.machine.up 4.877930 9.679320 -116.947750 -0.998440 -56.388020 -7.264720
#longs.machine 5.176320 26.137569 -122.273323 -1.489750 -34.609680 -6.889580
#longs.ok 31.956150 39.942261 -109.067177 -3.841700 -33.355869 -31.666140
#longs.ng 47.924129 29.784300 -129.056213 -6.845800 -22.939449 -44.537041
#drop 29.625290 34.349491 -110.810089 0.569530 -34.822540 154.066864
#longs.machine.u 4.877930 9.679321 -116.947754 -0.998438 -56.388016 -7.264723
#nullp 39.517384 31.322756 -94.699982 -117.035172 122.891006 344.040375
#pre 9.166110 37.979740 -81.726318 0.343650 -60.154953 174.817657
#rtchome1 -14.592921 -20.513672 -122.979691 5.037891 -76.092690 108.189819
.END
.REALS
tyterm = 1
tcp.port = 48569
tcp.connect.tmo = 5
tcp.receive.tmo = 5
tcp.send.tmo = 5
tcp.retry.count = 5
tcp.abort = 0
a.value = 0
ip[1] = 192
ip[2] = 168
ip[3] = 0
ip[4] = 163
o.value = 0
t.value = 1
tcp.error.cnt = 0
tcp.socket = 36
x.value = 0.5
y.value = 0
z.value = 0
motion.enable = 0
a = 0
active = -1
allow.motion = 0
angel = 0
clamp_open = 1009
clport = 48569
coord_add = 2002
debug = -1
deltax = 200
erx = -34009
extrax = 0
flagx = 0
is_moving = 2003
jt1.value = 40.76
jt2.value = 14.94
jt3.value = -128.81
jt4.value = -122.94
jt5.value = 109.19
jt6.value = 311.64
mjoint.enable = 0
mtdraw.enable = 0
num = 0
rc = -34025
sh = 10
shiftz = -12
skip = 0
socket_id = -34024
socketid = 36
speed1 = 30
speed2 = 10
speedmm = 50
tcp_conn_time = 10
tcp_port = 48569
tcp_recv_time = 15
tcp_send_time = 10
tool.value = 680
upd.tool = 0
x = 105.5
y = 116
.END
.STRINGS
$tcp.ip = "127.0.0.1"
$cmd = "GET_STATE"
$tcp.ip.copy = ""
$type = "LOLIZE"
.END
