using UnityEngine;
using System.Collections;
#if UNITY_EDITOR
using UnityEditor;
#endif
using UnityEngine.UI;
using System.IO;
using System;

public class ScarJoGUI : MonoBehaviour {

    public SpiderController spider;
    public string selectedSequence;
    public int repeatCount = 1;
    Vector3 camStartAngle;

    Text selectedSeqText;
    //Text selectedLegText;

    Text browseButtontext, executeButtontext, stopButtontext, editButtontext;
    InputField sequenceEditor;

    public bool editMode = false;
    public int delayval = 0;


	// Use this for initialization
	void Start () {
        camStartAngle = this.transform.eulerAngles;
        

        selectedSeqText = GameObject.Find("SelectedSequenceText").GetComponentInChildren<Text>();
        browseButtontext    = GameObject.Find("BrowseButton").GetComponentInChildren<Text>();
        executeButtontext   = GameObject.Find("ExecuteButton").GetComponentInChildren<Text>();
        stopButtontext = GameObject.Find("StopButton").GetComponentInChildren<Text>();
        editButtontext = GameObject.Find("EditButton").GetComponentInChildren<Text>();
        sequenceEditor = GameObject.Find("SequenceEditor").GetComponent<InputField>();

        browseButtontext.text = "Browse..";
        executeButtontext.text = "Execute Sequence";
        editButtontext.text = "EditMode";


        if (!File.Exists("tmpseq.txt"))
        {
            File.Create("tmpseq.txt");
        }
        selectedSequence = "tmpseq.txt";
        selectFile(selectedSequence);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

    public void toggleEditMode()
    {
        editMode = !editMode;
        spider.setEditMode(editMode);
        if (!editMode) editButtontext.text = "EditMode";
        else editButtontext.text = "AnimateMode";

        Camera.main.GetComponent<EditorCamera>().enabled = editMode;
    }

    public void browseForFile()
    {
		#if UNITY_EDITOR
        string path = EditorUtility.OpenFilePanel("Select sequence file", "\\", "txt");
        selectFile(path);
		#endif
    }

    public void selectFile(string filePath)
    {
        if (File.Exists(filePath))
        {

            selectSequence(filePath);
            StreamReader sr = new StreamReader(filePath);
            string content = sr.ReadToEnd();
            sr.Close();

            sequenceEditor.text = content;

            StreamWriter sw = new StreamWriter(filePath + ".bak", false);
            sw.Write(content);
            sw.Close();
        }
    }

    public void selectSequence(string path)
    {
        selectedSequence = path;
        selectedSeqText.text = path;

    }

    public void delayChanged(string delay)
    {
        delayval = int.Parse(delay);
    }

    public void insertDelay()
    {
        sequenceEditor.text = sequenceEditor.text.Insert(sequenceEditor.caretPosition, Environment.NewLine + "delay " + delayval + Environment.NewLine);
    }

    public void insertState()
    {
		sequenceEditor.text += "beginframe" + Environment.NewLine;
        foreach (SpiderLeg leg in spider.legs)
        {
            sequenceEditor.text += leg.getSequenceString(100);
        }
		sequenceEditor.text += Environment.NewLine + "frameend" + Environment.NewLine;
    }

    public void stopSequence()
    {
        spider.StopAllCoroutines();
    }

    public void playSelectedSequence()
    {
		spider.executeSequenceString(sequenceEditor.text, false, repeatCount, spider.delayModifier);
    }

    public void loopCountChanged(float val)
    {
        this.repeatCount = (int)val;
    }

    public void camSliderChanged(float val)
    {
        spider.delayModifier = (val * 10);
    }

    public void saveSequence()
    {
        StreamWriter sw = new StreamWriter(selectedSeqText.text, false);
        sw.Write(sequenceEditor.text);
        sw.Close();
    }

    public void sequenceEditDone(string newContent)
    {
		Debug.Log ("Sequence edit done!");
        //saveSequence();
    }
}
