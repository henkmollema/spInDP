using UnityEngine;
using System.Collections;
using System.IO;
using System;



public class SpiderController : MonoBehaviour
{
    
    
    // Based on physical dimensions of scarJo
    const float a = 11.0f; //Femur length (cm)
    const float c = 15.0f; //Tibia (cm)
    const float e = 6.85f; //height (cm)
    const float d = 12.24f;//Horz. afstand van c tot a (cm)
    const float lc = 4.107f; //Lengte coxa (cm)
    float b = (float)Math.Sqrt(Math.Pow(e,2) + Math.Pow(d, 2)); //diagonal (cm)

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
                if (line.TrimStart(' ').StartsWith("#")) continue;
                string cleanline = line.Replace("\r", string.Empty);
                string[] words = cleanline.Split(' ');


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

                else

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
                        Debug.Log("Will control servo " + legID + ", coords: " + newAngle + ", speed: " + speed);

                        setServoPos(float.Parse(coords[0]), float.Parse(coords[0]), float.Parse(coords[0]), legID, speed);


                        //vLeg = self.getServoPos(float(coords[0]), float(coords[1]), float(coords[2]), legID, s)
                        //self.servoController.move((legID - 1) * 3 + 1, vLeg.coxa, vLeg.coxaSpeed)
                        //self.servoController.move((legID - 1) * 3 + 2, vLeg.femur, vLeg.femurSpeed)
                        //self.servoController.move((legID - 1) * 3 + 3, vLeg.tibia, vLeg.tibiaSpeed)


                    }
                }
                
            }
        }


    }

    private void setServoPos(float x, float y, float z, int legID, float speed)
    {
        float lIK = (float) Math.Sqrt(Math.Pow((d + lc + x), 2) + (Math.Pow(y, 2)));
        float dIK = lIK - lc;
        float bIK = (float) Math.Sqrt(Math.Pow((e + z), 2) + Math.Pow(dIK, 2));


        //int coxaServoId = (legID - 1) * 3 + 1;
        //int femurServoId = (legID - 1) * 3 + 2;
        //int tibiaServoId = (legID - 1) * 3 + 3;

        //# determine current position of servos
        float coxaCurr = this.legs[legID-1].getCoxa() - 360;//self.servoController.getPosition(coxaServoId)
        float femurCurr = this.legs[legID - 1].getFemur() - 360;//self.servoController.getPosition(femurServoId)
        float tibiaCurr = this.legs[legID - 1].getTibia() - 360;//self.servoController.getPosition(tibiaServoId)
        Debug.Log(("current positions: " + coxaCurr + ", " + femurCurr + ", " + tibiaCurr));


        float alphaIK = (float) Math.Acos((Math.Pow(bIK, 2) + Math.Pow(c, 2) - Math.Pow(a, 2)) / (2 * bIK * c));
        float betaIK = (float) Math.Acos((Math.Pow(a, 2) + Math.Pow(c, 2) - Math.Pow(bIK, 2)) / (2 * a * c));
        float gammaIK = (float) Math.Acos((Math.Pow(a, 2) + Math.Pow(bIK, 2) - Math.Pow(c, 2)) / (2 * a * bIK));
        float thetaIK = (float) Math.Asin(y / lIK);
        float tauIK = (float) Math.Atan(e / dIK);


        float angleCoxa = thetaIK * (float)(180 / Math.PI);
        float angleFemur = -((gammaIK - tauIK) * (float)(180 / Math.PI));
        float angleTibia = 180 - ((betaIK) * (float)(180 / Math.PI));


        float deltaCoxa = Math.Abs(angleCoxa - coxaCurr);
        float deltaFemur = Math.Abs(angleFemur - femurCurr);
        float deltaTibia = Math.Abs(angleTibia - tibiaCurr);
        Debug.Log(("deltas " + deltaCoxa + ", " + deltaFemur + ", " + deltaTibia));


        float maxDelta = Math.Max(deltaCoxa, deltaFemur);
        maxDelta = Math.Max(deltaFemur, deltaTibia);

        float coxaSpeed = 0, femurSpeed = 0, tibiaSpeed = 0;

        if (maxDelta == deltaCoxa) {
            Debug.Log(("max delta is coxa"));
            coxaSpeed = speed;
            femurSpeed = (int)(Math.Round(speed * (deltaFemur / maxDelta), 0));
            tibiaSpeed = (int)(Math.Round(speed * (deltaTibia / maxDelta), 0));
        }
        else if (maxDelta == deltaFemur)
        {
            Debug.Log(("max delta is femur"));
            coxaSpeed = (int)(Math.Round(speed * (deltaCoxa / maxDelta), 0));
            femurSpeed = speed;
            tibiaSpeed = (int)(Math.Round(speed * (deltaTibia / maxDelta), 0));
        }
        else if (maxDelta == deltaTibia)
        {
            Debug.Log(("max delta is tibia"));
            coxaSpeed = (int)(Math.Round(speed * (deltaCoxa / maxDelta), 0));
            femurSpeed = (int)(Math.Round(speed * (deltaFemur / maxDelta), 0));
            tibiaSpeed = speed;
        }

        Debug.Log(("angleCoxa: " + angleCoxa + " speed: " + coxaSpeed));
        Debug.Log(("angleFemur: " + angleFemur + " speed: " + femurSpeed));
        Debug.Log(("angleTibia: " + angleTibia + " speed: " + tibiaSpeed));


        this.legs[legID - 1].setCoxa(angleCoxa, coxaSpeed);
        this.legs[legID - 1].setFemur(angleFemur, femurSpeed);
        this.legs[legID - 1].setTibia(angleTibia, tibiaSpeed);

    }



}
