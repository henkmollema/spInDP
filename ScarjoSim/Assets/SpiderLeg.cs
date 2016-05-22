using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;

public class SpiderLeg : MonoBehaviour
{
    public struct LegMovement
    {
        public bool valid;
        public bool empty;
        public float coxa, tibia, femur;
        public float coxaSpeed, tibiaSpeed, femurSpeed;
        public float maxExecTime;
    }

    public struct SequenceFrame
    {
        public Dictionary<int, LegMovement> movements;
        public float maxMaxExecTime;
    }

    public static SequenceFrame newSequenceFrame(Dictionary<int, LegMovement> movements)
    {
        SequenceFrame retVal = new SequenceFrame();
        float maxTime = 0f;
        foreach(KeyValuePair<int, LegMovement> k in movements)
        {
            maxTime = Mathf.Max(maxTime, k.Value.maxExecTime);
        }
        retVal.maxMaxExecTime = maxTime;

        Dictionary<int, LegMovement> scaledMoves = new Dictionary<int, LegMovement>();
        foreach (KeyValuePair<int, LegMovement> mov in movements)
        {
            float scaleFactor = mov.Value.maxExecTime / retVal.maxMaxExecTime;

            if (retVal.maxMaxExecTime == 0)
                scaleFactor = 0;
            

            LegMovement newMov = new LegMovement();
            newMov.coxa = mov.Value.coxa;
            newMov.tibia = mov.Value.tibia;
            newMov.femur = mov.Value.femur;

            newMov.coxaSpeed = mov.Value.coxaSpeed * scaleFactor;
            newMov.tibiaSpeed = mov.Value.tibiaSpeed * scaleFactor;
            newMov.maxExecTime = mov.Value.maxExecTime * scaleFactor;

            scaledMoves.Add(mov.Key, newMov);
        }

        retVal.movements = scaledMoves;

        return retVal;
    }

    public int legID;
    Transform Coxa, Femur, Tibia;

    Quaternion cTarget, fTarget, tTarget;
    public Quaternion lastCoxa, lastFemur, lastTibia;
    float cFinish, fFinish, tFinish;
    //float cStart, fStart, tStart;
    float startTime;
    public float maxExecTime;

    List<LegMovement> queue = new List<LegMovement>();

    public static float anglePerSecond = 33f; //114rpm at max speed in specification
    public float angleOffsetY = 0f;

    bool emptyMove = false;

    bool cChanged, fChanged, tChanged;

    public bool shouldAnimate = true;
    // Use this for initialization
    void Start()
    {
        Coxa = this.transform;
        Femur = this.transform.Find("femur");
        Tibia = Femur.Find("tibia");

        lastCoxa = Coxa.localRotation;
        lastFemur = Femur.localRotation;
        lastTibia = Tibia.localRotation;

        cTarget = Coxa.localRotation;
        fTarget = Femur.localRotation;
        tTarget = Tibia.localRotation;

        angleOffsetY = this.transform.localRotation.eulerAngles.y;
    }

    // Update is called once per frame
    void Update()
    {
        if (!shouldAnimate) return;

        //Debug.Log("Anim: " + (cFinish - cStart));
        //Debug.Log("Anim: " + ((Time.time - cStart) / (cFinish - cStart)));
        //Debug.Log("Anim: " + (Time.time - startTime) );
        float ratio = 0f;
        if (maxExecTime == 0)
            ratio = 1.1f;
        else
            ratio = ((Time.time - startTime) / maxExecTime);

        if(ratio  <= 1)
        {
            //Debug.Log("Anim: " + ((Time.time - cStart) / (cFinish - cStart)));
            if ( !emptyMove)
            {
                //Mathf.LerpAngle()
                Quaternion newCoxa = Quaternion.Lerp(lastCoxa, cTarget, ratio);
                Coxa.transform.localRotation = newCoxa;
            }

            if (!emptyMove)
            {
                Quaternion newFemur = Quaternion.Lerp(lastFemur, fTarget, ratio);
                Femur.transform.localRotation = newFemur;
            }

            if (!emptyMove)
            {
                Quaternion newTibia = Quaternion.Lerp(lastTibia, tTarget, ratio);
                Tibia.transform.localRotation = newTibia;
            }
        }
        else
        {
            LegMovement nextMove = getNextMove();
            if (nextMove.valid)
            {
                maxExecTime = nextMove.maxExecTime;
                startTime = Time.time;
                if(!nextMove.empty)
                {
                    //Debug.Log("New Move: " + nextMove.coxa + ", " + fixAngle(nextMove.femur) + ", " + nextMove.tibia + " EXECTIME: " + nextMove.maxExecTime);
                    setCoxa(nextMove.coxa, nextMove.coxaSpeed);
                    setFemur(nextMove.femur, nextMove.femurSpeed);
                    setTibia(nextMove.tibia, nextMove.tibiaSpeed);
                    emptyMove = false;
                }
                else{
                    emptyMove = true;
                }
            }

        }

    }

    public LegMovement getNextMove()
    {
        LegMovement retVal = new LegMovement();
        if (queue.Count > 0)
        {
            retVal = queue[0];
            retVal.valid = true;
            queue.RemoveAt(0);
        }

        return retVal;
    }

    public string getSequenceString(float speed)
    {
        string retVal = "" + Environment.NewLine;
        int firstServo = ((legID - 1) * 3) + 1;

        retVal += "s:" + firstServo + " " + (int)getCoxa() + ",0,0 " + speed + Environment.NewLine;
        retVal += "s:" + (firstServo + 1) + " " + (int)getFemur() + ",0,0 " + speed + Environment.NewLine;
        retVal += "s:" + (firstServo + 2) + " " + (int)getTibia() + ",0,0 " + speed + Environment.NewLine;

        return retVal;
    }

    public float getCoxa()
    {
        return Coxa.transform.localRotation.eulerAngles.y - angleOffsetY;
    }

    public float getFemur()
    {
        return Femur.transform.localRotation.eulerAngles.z;
    }

    public float getTibia()
    {
        return Tibia.transform.localRotation.eulerAngles.z;
    }

    public void addMove(LegMovement lm)
    {
        queue.Add(lm);
    }

    public bool hasMovesOnQueue()
    {
        return queue.Count > 0;
    }

    private float fixAngle(float a)
    {
        return a;
    }

    public float setCoxa(float angle, float speed)
    {
        
        lastCoxa = cTarget;
        cTarget = Quaternion.Euler(0, fixAngle(angle + angleOffsetY), 0);
        float distance = Math.Abs(Quaternion.Angle(cTarget, Coxa.localRotation));
        
        //cStart = Time.time;
        //Debug.Log("distabce: " + distance);
        cFinish = Time.time + ((distance) / (anglePerSecond * (speed / 1024f)));

        return distance;
    }

    public float setFemur(float angle, float speed)
    {
        lastFemur = fTarget;
        fTarget = Quaternion.Euler(0, 0, fixAngle(angle));
        float distance = Quaternion.Angle(fTarget, Femur.localRotation);
        //fStart = Time.time;
        //Debug.Log("distabce: " + ((distance * (180f / Mathf.PI)) / (anglePerSecond * (speed / 1024f))));
        fFinish = Time.time + ((distance) / (anglePerSecond * (speed / 1024f)));

        return distance;
    }

    public float setTibia(float angle, float speed)
    {

        lastTibia = tTarget;
        tTarget = Quaternion.Euler(0, 0, fixAngle(angle));
        float distance =  Quaternion.Angle(cTarget, Tibia.localRotation);
        //tStart = Time.time;
        //Debug.Log("distabce: " + ((distance) / (anglePerSecond * (speed / 1024f))));
        tFinish = Time.time + (((distance) / anglePerSecond) * (speed / 1024f));

        return distance;
    }


    public void moveByServoID(int servoID, float angle, float speed, bool allLegs)
    {
        if (!allLegs && servoID - ((legID - 1) * 3) < 0) return; //If it's not this leg we need

        int switchValue = servoID - ((legID - 1) * 3);
        if (allLegs) switchValue = servoID % 3;

        float distance =  0f;
        startTime = Time.time;
        switch (switchValue)
        {
            case 1:
                distance = setCoxa(angle, speed);
                break;

            case 2:
                distance = setFemur(angle, speed);
                break;

            case 3:
                distance = setTibia(angle, speed);
                break;
        }

        this.maxExecTime = Mathf.Max(this.maxExecTime, (((distance) / anglePerSecond) * (speed / 1024f)));

    }
}
