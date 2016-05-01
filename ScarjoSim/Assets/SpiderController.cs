using UnityEngine;
using System.Collections;
using System.IO;

public class SpiderController : MonoBehaviour
{

    public SpiderLeg[] legs;

    string currentSequence;

    public float delayModifier = 1f;

    // Use this for initialization
    void Start()
    {
        legs = new SpiderLeg[6];
        for (int i = 0; i < legs.Length; i++)
        {
            legs[i] = this.transform.Find("leg" + (i + 1).ToString()).gameObject.GetComponent<SpiderLeg>();
            legs[i].legID = i + 1;

        }

        
        //executeSequence("D:\\Projecten\\spInDP\\sequences\\unity-test.txt", false, 100);
    }

    bool firstTick = true;
    // Update is called once per frame
    void Update()
    {
        if(firstTick)
        {
            firstTick = false;
            //executeSequence("D:\\Projecten\\spInDP\\sequences\\startup.txt", false, 1, false);
        }

        if(Input.GetKeyDown(KeyCode.W))
        {
            //executeSequence("D:\\Projecten\\spInDP\\sequences\\walk-all-legs.txt", false, 1, false);
            //executeSequence("D:\\Projecten\\spInDP\\sequences\\test-all-servo.txt", false, 1, false);

        }
    }

    public void executeSequence(string filepath, bool validate, int repeat, bool allLegs)
    {
        currentSequence = filepath;
        StartCoroutine(parseSequence(filepath, validate, repeat, allLegs));
    }

    public void setEditMode(bool enabled)
    {
        foreach(SpiderLeg l in legs)
        {
            l.shouldAnimate = !enabled;
        }
    }


    /**
    **  Sequence parsing logic, use executeSequence() to run a sequence file
    **/
    IEnumerator parseSequence(string filePath, bool validate, int repeat, bool allLegs)
    {

        Debug.Log("Parsing sequence at: " + currentSequence);
        bool hasHeader = false;
        int lineNr = 0;
        //string line;
        StreamReader theReader = new StreamReader(currentSequence, System.Text.Encoding.Default);
        string filecontent = theReader.ReadToEnd();
        theReader.Close();
        string[] lines = filecontent.Split('\n');

        for (int i = 0; i < repeat; i++)
        {
            foreach (string line in lines)
            {
                lineNr += 1;
                string[] words = line.Split(' ');

                if (!hasHeader && !words[0].ToLower().Equals("sequence"))
                {
                    Debug.Log("Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'");
                    yield break;
                }
                else if (lineNr == 1)
                {
                    hasHeader = true;
                    continue;
                }

                if (words[0].ToLower().Equals("delay"))
                {
                    if (words.Length != 2)
                    {
                        Debug.Log("No argument given for delay at line: " + lineNr);
                        yield break;
                    }

                    float seconds = int.Parse(words[1]) / 1000f;


                    if (!validate)
                    {
                        Debug.Log("Will delay " + seconds + " seconds");
                        yield return new WaitForSeconds(seconds * delayModifier);
                    }

                }



                if (words[0].ToLower().StartsWith("s:"))
                {
                    if (words.Length < 2 || words.Length > 3)
                    {
                        Debug.Log("Wrong amount of arguments for servo control: " + words.Length + " at line: " + lineNr);
                        yield break;
                    }

                    int servoID = int.Parse(words[0].Split(':')[1]);
                    string[] coords = words[1].Split(',');
                    if (coords.Length != 3)
                    {
                        Debug.Log("Wrong amount of coords: " + coords.Length + " at line: " + lineNr);
                        yield break;
                    }

                    int speed = -1;
                    if (words.Length == 3)
                    {
                        speed = int.Parse(words[2]);
                    }

                    if (!validate)
                    {
                        float newAngle = float.Parse(coords[0]);
                        Debug.Log("Will control servo " + servoID + ", coords: " + newAngle + ", speed: " + speed);
                        foreach(SpiderLeg leg in legs)
                        {
                            
                            leg.moveByServoID(servoID, newAngle, speed, allLegs);
                        }
                        //#hier de servocontroller aanroepen met de variabelen wanneer not validate
                    }
                }

            }
        }


    }

    

}
