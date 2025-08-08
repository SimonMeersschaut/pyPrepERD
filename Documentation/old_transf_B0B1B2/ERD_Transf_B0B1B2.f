	program ApplyTransformation
	
c! Bparams starting with channel 904, covers 5329 channels (i.e. till 6233)
 	
	character*132 filenaam, cmdlineargument
	character*200 line
	integer*4 ToFchmin,ToFchmax
	integer*4 calfound
	real*8 B0(8192)
	real*8 B1(8192)
	real*8 B2(8192)
	real*8 time_in_ns,chi2
	integer*4 ch,ToFch,Ench,Iso_ch
	integer*4 nrlines,effnrlines
	real*8 ToFns,Iso_amu
	real*8 ns_ch,t_offs

	calfound = 0
	ToFchmin = 1
	ToFchmax = 8192

	call getarg(1,cmdlineargument)
	filenaam = cmdlineargument

	open(unit=8,file='Bparams.txt',status='unknown')
	do 100 i = ToFchmin,ToFchmax
	  read(8,200)line
200	Format(A200)
	  read(line,*)ch,time_in_ns,B0(i),B1(i),B2(i),Chi2
100	continue
	close(unit=8)
	goto 102
	
901	write(6,*)'error opening Bparams.txt'
	write(6,*)' '
	write(6,*)'  please verify if it was copied by _set_params.bat'
	write(6,*)'  if not, check if you have network access'
	write(6,*)' '
	goto 999

102	open(unit=18,file='tof.in',status='old',err=180)
	do while(.TRUE.)
	read(18,200,err=180,end=180)line
	if (index(line,'TOF calibration').ne.0) then
		myindex = index(line,':')
		read(line(myindex+1:200),*) ns_ch,t_offs
		calfound = 1
		goto 180
	endif
	end do
180	continue
	close(unit=18)	

	If (calfound.eq.1) then
		write(6,66)'      ns_ch : ',ns_ch,'    t_offs : ',t_offs
66		format(A14,E11.4,A13,E11.4)		
	else
		write(6,*)'calibration not found in Tof.in'
		read(5,*)
	endif	
	
	open(unit=11,file=filenaam,status='unknown')
	open(unit=12,file='tmp.ext',status='unknown')
	  nrlines=0
	  effnrlines=0
	  read(11,*,err=500)ToFch,Ench
	  nrlines = nrlines+1
	do while(.TRUE.)
	  if(ToFch.ge.ToFchmin .and. ToFch.le.ToFchmax) then
	  ToFns=1.E+09*(t_offs+ns_ch*real(ToFch));
	  Iso_amu = B0(ToFch) + B1(ToFch)*Ench + 
     &		B2(ToFch)*Ench*Ench
	  Iso_ch = max(1,min(9999,int(Iso_amu*100. +0.5)))
	  write(12,120)ToFch,' ',ToFns,' ',Ench,' ',Iso_amu,' ',Iso_ch
120	format(I7,A1,F12.3,A1,I7,A1,F11.4,A1,I7,A1)
	  effnrlines = effnrlines+1
	  endif
	  read(11,*,end=500,err=500)ToFch,Ench
	  nrlines = nrlines+1
	end do
500	continue
	close(unit=11)
	close(unit=12)
	write(6,*) nrlines,' nrlines have been read'
	write(6,*) '    mass artificially limited min 0.02 - max 99 amu'
	write(6,*) effnrlines,' effective lines written between '
     +		,'TOFchmin and TOFchmax'
	write(6,*)
999	return
	end