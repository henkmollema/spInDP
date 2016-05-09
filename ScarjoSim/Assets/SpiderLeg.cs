using UnityEngine;
using System.Collections;
using System;

public class SpiderLeg : MonoBehaviour {

    public int legID;
    Transform Coxa, Femur, Tibia;

    Quaternion cTarget, fTarget, tTarget;
    float cFinish, fFinish, tFinish;
    float cStart, fStart, tStart;

    public float anglePerSecond = (180 * 360) / 60; //114rpm at max speed in specification
    public float angleOffsetY = 0f;

    bool cChanged, fChanged, tChanged;

    public bool shouldAnimate = true;
    // Use this for initialization
    void Start () {
        Coxa = this.transform;
        Femur = this.transform.Find("femur");
        Tibia = Femur.Find("tibia");

        cTarget = Coxa.localRotation;
        fTarget = Femur.localRotation;
        tTarget = Tibia.localRotation;

        angleOffsetY = this.transform.localRotation.eulerAngles.y;
    }
	
	// Update is called once per frame
	void Update () {
        if (!shouldAnimate) return;

        if (Coxa.transform.localRotation != cTarget)
        {
            Quaternion newCoxa = Quaternion.Lerp(Coxa.transform.localRotation, cTarget, (Time.time - cStart) / (cFinish - cStart));
            Coxa.transform.localRotation = newCoxa;

        }

        if (Femur.transform.localRotation != fTarget)
        {
            Quaternion newFemur = Quaternion.Lerp(Femur.transform.localRotation, fTarget, (Time.time - fStart) / (fFinish - fStart));
            Femur.transform.localRotation = newFemur;
        }

        if (Tibia.transform.localRotation != tTarget)
        {

            Quaternion newTibia = Quaternion.Lerp(Tibia.transform.localRotation, tTarget, (Time.time - tStart) / (tFinish - tStart));
            Tibia.transform.localRotation = newTibia;
        }

    }

    

    public string getSequenceString(float speed)
    {
        string retVal = "" + Environment.NewLine;
        int firstServo = ((legID - 1) * 3) + 1;

        retVal += "s:" + firstServo + " " + (int)getCoxa() + ",0,0 " + speed + Environment.NewLine;
        retVal += "s:" + (firstServo+1) + " " + (int)getFemur() + ",0,0 " + speed + Environment.NewLine;
        retVal += "s:" + (firstServo+2) + " " + (int)getTibia() + ",0,0 " + speed + Environment.NewLine;

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

    public void setCoxa(float angle, float speed)
    {
        cTarget = Quaternion.Euler(0,angle + angleOffsetY, 0);
        float distance = Quaternion.Angle(cTarget, Coxa.localRotation);
        cStart = Time.time;
        
        cFinish = Time.time + (distance / (anglePerSecond * (speed / 1024f)));
    }

    public void setFemur(float angle, float speed)
    {
        fTarget = Quaternion.Euler(0, 0, angle );
        float distance = Quaternion.Angle(fTarget, Femur.localRotation);
        fStart = Time.time;
        fFinish = Time.time + (distance / (anglePerSecond * (speed / 1024f)));
    }

    public void setTibia(float angle, float speed)
    {
        tTarget = Quaternion.Euler(0, 0, angle);
        float distance = Quaternion.Angle(cTarget, Tibia.localRotation);
        tStart = Time.time;

        tFinish = Time.time + (distance / (anglePerSecond * (speed / 1024f)));
    }

    
    public void moveByServoID(int servoID, float angle, float speed, bool allLegs) {
        if (!allLegs && servoID - ((legID - 1) * 3) < 0) return; //If it's not this leg we need

        int switchValue = servoID - ((legID - 1) * 3);
        if (allLegs) switchValue = servoID % 3;

        switch (switchValue)
        {
            case 1:
                setCoxa(angle, speed);
                break;

            case 2:
                setFemur(angle, speed);
                break;

            case 3:
                setTibia(angle, speed);
                break;
        }

    }
}
