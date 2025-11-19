'=== Class Module: CAppEvents ===
Option Explicit

Public WithEvents PPTEvent As Application


' ===================================
' Event: SlideShowBegin
' FIX: Fires when the slideshow starts (i.e., when the first slide is shown).
' ===================================
Private Sub PPTEvent_SlideShowBegin(ByVal Wn As SlideShowWindow)
    On Error GoTo EH

    Dim currentNotes As String
    
    ' Get the slide object for the currently displayed slide (the first one)
    currentNotes = modHttpNotes.GetNotesText(Wn.View.Slide)

    Debug.Print "=== SlideShowBegin ==="
    Debug.Print "Current slide position: " & Wn.View.CurrentShowPosition
    Debug.Print "Notes length: " & Len(currentNotes) & " chars"
    Debug.Print "Notes content: " & Left$(currentNotes, 100) & IIf(Len(currentNotes) > 100, "...", "")

    If Len(Trim$(currentNotes)) = 0 Then
        Debug.Print "WARNING: No notes on this slide"
    Else
        ' Call into the standard module to send the HTTP request
        Debug.Print "Calling SetWelcome..."
        modHttpNotes.SetWelcome currentNotes
    End If

    Exit Sub
EH:
    Debug.Print "? PPTEvent_SlideShowBegin error: "; Err.Number; " - "; Err.Description
End Sub


' ===================================
' Event: SlideShowNextSlide
' Fires when moving to the 2nd slide and every slide thereafter.
' ===================================
Private Sub PPTEvent_SlideShowNextSlide(ByVal Wn As SlideShowWindow)
    On Error GoTo EH

    Dim currentNotes As String
    currentNotes = modHttpNotes.GetNotesText(Wn.View.Slide)

    Debug.Print "=== SlideShowNextSlide ==="
    Debug.Print "Current slide position: " & Wn.View.CurrentShowPosition
    Debug.Print "Notes length: " & Len(currentNotes) & " chars"
    Debug.Print "Notes content: " & Left$(currentNotes, 100) & IIf(Len(currentNotes) > 100, "...", "")

    If Len(Trim$(currentNotes)) = 0 Then
        Debug.Print "WARNING: No notes on this slide"
    Else
        ' Call into the standard module to send the HTTP request
        Debug.Print "Calling SetWelcome..."
        modHttpNotes.SetWelcome currentNotes
    End If

    Exit Sub
EH:
    Debug.Print "? PPTEvent_SlideShowNextSlide error: "; Err.Number; " - "; Err.Description
End Sub

