using UnityEngine;
using System.Collections;
using System.IO;
using System;
using System.Collections.Generic;

public class SpiderController : MonoBehaviour
{


    // Based on physical dimensions of scarJo
    public static float a = 11.0f; //Femur length (cm)
	public static float c = 15.0f; //Tibia (cm)
	public static float e = 5.60f; //height (cm)
	public static float d = 12.24f;//Horz. afstand van c tot a (cm)
	public static float lc = 4.107f; //Lengte coxa (cm)
    float b = (float)Math.Sqrt(Math.Pow(e, 2) + Math.Pow(d, 2)); //diagonal (cm)

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
        if (firstTick)
        {
            firstTick = false;
            //executeSequence("D:\\Projecten\\spInDP\\sequences\\startup.txt", false, 1, false);
        }

        if (Input.GetKeyDown(KeyCode.W))
        {
            //executeSequence("D:\\Projecten\\spInDP\\sequences\\walk-all-legs.txt", false, 1, false);
            //executeSequence("D:\\Projecten\\spInDP\\sequences\\test-all-servo.txt", false, 1, false);

        }
    }

    public void executeSequenceString(string seqString, bool validate, int repeat, float speedModifier)
    {
		StartCoroutine(parseSequence(seqString, validate, repeat, speedModifier));
    }

    public void setEditMode(bool enabled)
    {
        foreach (SpiderLeg l in legs)
        {
            l.shouldAnimate = !enabled;
        }
    }

	void executeSequence(string filePath, bool validate, int repeat, float speedModifier)
	{
		Debug.Log("Parsing sequence at: " + currentSequence);

		StreamReader theReader = new StreamReader(currentSequence, System.Text.Encoding.Default);
		string filecontent = theReader.ReadToEnd();
		theReader.Close();

		StartCoroutine(parseSequence (filecontent, validate, repeat, speedModifier));

	}


    /**
    **  Sequence parsing logic, use executeSequence() to run a sequence file
    **/
    IEnumerator parseSequence(string filecontent, bool validate, int repeat, float speedModifier)
    {
		bool hasHeader = false;
		int lineNr = 0;
        
        string[] lines = filecontent.Split('\n');
        Dictionary<int, SpiderLeg.LegMovement> tmpFrame = null;
        int tmpFrameMillis = -1;

        for (int i = 0; i < repeat; i++)
        {
            foreach (string line in lines)
            {
                lineNr += 1;
                if (line.TrimStart(' ').StartsWith("#")) continue;
                string cleanline = line.Replace("\r", string.Empty);
                string[] words = cleanline.Split(' ');
                string command = words[0];


                if (!hasHeader && !words[0].ToLower().Equals("sequence"))
                {
                    Debug.Log("Sequencefile has an invalid header, it should start with 'Sequence <sequencename>'");
                    yield break;
                }
                else if (lineNr == 1)
                {
                    hasHeader = true;
                    if(words.Length > 3)
                    {
                        this.offset = int.Parse(words[3]);
                    }
                    else
                    {
                        this.offset = 0;
                    }
                    continue;
                }

                if (speedModifier < 0)
                {
                    if (command == "framebegin")
                        command = "frameend";
                    else if (command == "frameend")
                        command = "framebegin";
                }

                if (words[0].ToLower().Equals("framebegin"))
                {
                    if(words.Length > 1)
                    {
                        tmpFrameMillis = int.Parse(words[1]);
                    }

                    tmpFrame = new Dictionary<int, SpiderLeg.LegMovement>();
                    
                }
                else
                if (words[0].ToLower().Equals("frameend"))
                {
                    if(tmpFrame == null)
                        continue;

                    SpiderLeg.SequenceFrame sf = SpiderLeg.newSequenceFrame(tmpFrame, tmpFrameMillis);
                    tmpFrameMillis = -1;

                    for (int x = 1; x < 7; x++)
                    {
                        SpiderLeg.LegMovement mov;
                        bool hasMov = sf.movements.TryGetValue(x, out mov);
                        if(!hasMov)
                        {
                            mov = new SpiderLeg.LegMovement();
                            mov.empty = true;
                        }
                        mov.maxExecTime = sf.maxMaxExecTime;
                        legs[x - 1].addMove(mov);
                    }

                    tmpFrame.Clear();
                    tmpFrame = null;
                }
                else
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
                else
                if (words[0].ToLower().StartsWith("waitlegs"))
                {
                    //bool shouldBlock = true;

                    bool allEmpty = false;

                    while (!allEmpty)
                    {
                        float maxExec = 0f;
                        foreach (SpiderLeg leg in legs)
                        {
                            allEmpty = true;
                            maxExec = Mathf.Max(maxExec, leg.maxExecTime);
                            if (leg.hasMovesOnQueue())
                            {
                                allEmpty = false;
                                yield return new WaitForSeconds(maxExec);
                            }
                        }
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

                    int speed = -1;
                    if (words.Length == 3)
                    {
                        speed = int.Parse(words[2]);
                    }

					speed = (int)(speed * speedModifier);

                    if (!validate)
                    {
                        float newAngle = float.Parse(coords[0]);
                        //Debug.Log("Will control servo " + servoID + ", coords: " + newAngle + ", speed: " + speed);
                        foreach (SpiderLeg leg in legs)
                        {
                            leg.moveByServoID(servoID, newAngle, speed, false);
                        }
                        //#hier de servocontroller aanroepen met de variabelen wanneer not validate
                    }
                }

                else
            //Controll legs
            if (words[0].ToLower().StartsWith("l:"))
                {
                    if (words.Length < 2 || words.Length > 3)
                    {
                        Debug.Log("Wrong amount of arguments for servo control: " + words.Length + " at line: " + lineNr);
                        yield break;
                    }

                    int legID = int.Parse(words[0].Split(':')[1]);
                    string[] coords = words[1].Split(",".ToCharArray());
                    if (coords.Length != 3)
                    {
                        Debug.Log("Wrong amount of coords: " + coords.Length + " at line: " + lineNr);
                        yield break;
                    }



                    int speed = -1;
                    if (words.Length == 3)
                    {
                        speed = (int)(int.Parse(words[2]));
                    }

					speed =(int)(speed * speedModifier);

                    if (!validate)
                    {

                        //Debug.Log("Will control leg " + legID + ", coords: " + words[1] + ", speed: " + speed);

                        SpiderLeg.LegMovement lm = setServoPos(float.Parse(coords[0]), float.Parse(coords[1]), float.Parse(coords[2]), legID, speed);
                        if(tmpFrame == null)
                        {
                            this.legs[legID - 1].addMove(lm);
                        }
                        else
                        {
                            tmpFrame.Add(legID, lm);
                        }
                    }
                }

            }
        }


    }
    float[] servoAngleMap = new float[18];
    float offset = 0f;
    private SpiderLeg.LegMovement setServoPos(float x, float y, float z, int legID, float speed)
    {

		if (legID == 1 || legID == 6 || legID == 5)
		{
			y *= -1;
		}

        float lIK = (float)Math.Sqrt(Math.Pow((d + lc + x), 2) + (Math.Pow(y, 2)));
        float dIK = lIK - lc;
        float bIK = (float)Math.Sqrt(Math.Pow((e + z), 2) + Math.Pow(dIK, 2));

        //# determine current position of servos
        float coxaCurr = servoAngleMap[((legID - 1) * 3)];//self.servoController.getPosition(coxaServoId)
        float femurCurr = servoAngleMap[((legID - 1) * 3) + 1];//self.servoController.getPosition(femurServoId)
        float tibiaCurr = servoAngleMap[((legID - 1) * 3) + 2]; ;//self.servoController.getPosition(tibiaServoId)
        //Debug.Log(("current positions: " + coxaCurr + ", " + femurCurr + ", " + tibiaCurr));


        //float alphaIK = (float) Math.Acos((Math.Pow(bIK, 2) + Math.Pow(c, 2) - Math.Pow(a, 2)) / (2 * bIK * c));
        float betaIK = (float)Math.Acos((Math.Pow(a, 2) + Math.Pow(c, 2) - Math.Pow(bIK, 2)) / (2 * a * c));
        float gammaIK = (float)Math.Acos((Math.Pow(a, 2) + Math.Pow(bIK, 2) - Math.Pow(c, 2)) / (2 * a * bIK));
        float thetaIK = (float)Math.Asin(y / lIK);
        float tauIK = (float)Math.Atan((e + z) / dIK);


        float angleCoxa = thetaIK * (180 / Mathf.PI);
        float angleFemur = -((gammaIK - tauIK) * (180 / Mathf.PI));
        float angleTibia = 180 - ((betaIK) * (180 / Mathf.PI)) ;

        if (legID == 1 || legID == 4)
        {
            angleCoxa -= offset;
        }
        else if (legID == 5 || legID == 2)
        {
            angleCoxa += offset;
        }

        float deltaCoxa = Quaternion.Angle(Quaternion.Euler(0, angleCoxa, 0), Quaternion.Euler(0, coxaCurr, 0));
		float deltaFemur = Quaternion.Angle(Quaternion.Euler(0, 0, angleFemur), Quaternion.Euler(0, 0, femurCurr));;//Math.Abs(angleFemur - femurCurr);
		float deltaTibia = Quaternion.Angle(Quaternion.Euler(0, 0, angleTibia), Quaternion.Euler(0, 0, tibiaCurr));//Math.Abs(angleTibia - tibiaCurr);
        Debug.Log(("deltas " + deltaCoxa + ", " + deltaFemur + ", " + deltaTibia));

        servoAngleMap[(legID - 1) * 3] = angleCoxa;
        servoAngleMap[(legID - 1) * 3 + 1] = angleFemur;
        servoAngleMap[(legID - 1) * 3 + 2] = angleTibia;

        float maxDelta = 0;
        maxDelta = Math.Max(deltaCoxa, deltaFemur);
        maxDelta = Math.Max(maxDelta, deltaTibia);

        if(maxDelta == 0)
        {
            //Debug.LogError("0 Delta moving to: " + x + "," + y + "," + z + " LEG: " + legID);
        }
        float coxaSpeed = 0, femurSpeed = 0, tibiaSpeed = 0;

        if(maxDelta != 0)
        {
            if (maxDelta == deltaCoxa)
            {
                //Debug.Log(("max delta is coxa"));
                coxaSpeed = speed;
                femurSpeed = (int)(Math.Round(speed * (deltaFemur / maxDelta), 0));
                tibiaSpeed = (int)(Math.Round(speed * (deltaTibia / maxDelta), 0));
            }
            else if (maxDelta == deltaFemur)
            {
                //Debug.Log(("max delta is femur"));
                coxaSpeed = (int)(Math.Round(speed * (deltaCoxa / maxDelta), 0));
                femurSpeed = speed;
                tibiaSpeed = (int)(Math.Round(speed * (deltaTibia / maxDelta), 0));
            }
            else if (maxDelta == deltaTibia)
            {
                //Debug.Log(("max delta is tibia"));
                coxaSpeed = (int)(Math.Round(speed * (deltaCoxa / maxDelta), 0));
                femurSpeed = (int)(Math.Round(speed * (deltaFemur / maxDelta), 0));
                tibiaSpeed = speed;
            }
        }
        
        

        //Debug.Log(("angleCoxa: " + angleCoxa + " speed: " + coxaSpeed));
        //Debug.Log(("angleFemur: " + angleFemur + " speed: " + femurSpeed));
        //Debug.Log(("angleTibia: " + angleTibia + " speed: " + tibiaSpeed));


        SpiderLeg.LegMovement lm = new SpiderLeg.LegMovement();
        lm.coxa = angleCoxa;
        lm.coxaSpeed = coxaSpeed;
        lm.femur = angleFemur;
        lm.femurSpeed = femurSpeed;
        lm.tibia = angleTibia;
        lm.tibiaSpeed = tibiaSpeed;
        
        float timePerAngle = (float)(100 * 360.0 / 60.0) * (speed / 1023f);
        lm.maxExecTime = maxDelta / timePerAngle;


        return lm;
    }



}
