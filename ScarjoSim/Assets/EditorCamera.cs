/* Copyright (c) 2009, Shane Yanke
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification, are permitted 
 * provided that the following conditions are met:
 * 
 *     * Redistributions of source code must retain the above copyright notice, this list of conditions and 
 * 	     the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and 
 * 	     the following disclaimer in the documentation and/or other materials provided with the distribution.
 *     * Neither the name of Cogmation Robotics nor the names of its contributors may be used to endorse or 
 * 	     promote products derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
 * USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *   Heavily edited to accomodate the rotation of the spider legs.
 */	


using UnityEngine;
using System.Collections;
using System;

public enum TransformType
{
	//Move	= 0,
	Rotate	= 1,
	//Scale	= 2
}

[RequireComponent(typeof(Camera))]
public class EditorCamera : MonoBehaviour
{
	public Material lineMaterial;
    public Material overlayMaterial;
    public Material gridMaterial;
	protected static Color colorLightBlue = new Color( 0.59f, 0.71f, 0.89f, 1.0f );
	protected static Color colorLightGreen = new Color( 0.58f, 0.87f, 0.56f, 1.0f );
	
	protected static Color HandleColorX = Color.red;
	protected static Color HandleColorY = Color.green;
	protected static Color HandleColorZ = Color.blue;
	
	protected static Vector3 xHandleBoxMin = new Vector3(0,-0.005f,-0.005f);
	protected static Vector3 xHandleBoxMax = new Vector3(0.1f,0.01f,0.01f);
	protected static Vector3 yHandleBoxMin = new Vector3(-0.005f,0,-0.005f);
	protected static Vector3 yHandleBoxMax = new Vector3(0.01f,0.1f,0.01f);
	protected static Vector3 zHandleBoxMin = new Vector3(-0.005f,-0.005f,0);
	protected static Vector3 zHandleBoxMax = new Vector3(0.01f,0.01f,0.1f);
	
	protected static Transform SelectedTransform;
	protected static GameObject SelectedObject;
	
	protected static TransformType currTransformType = TransformType.Rotate;
	
	public enum RotationAxes { None = 0, MouseX = 1, MouseY = 2, MouseXAndY = 3 }
	public RotationAxes axes = RotationAxes.MouseXAndY;
	public bool zoom = true;
	
	public float sensitivityX = 3F;
	public float sensitivityY = 3F;

	public float minimumX = -360F;
	public float maximumX = 360F;

	public float minimumY = -60F;
	public float maximumY = 60F;

	protected float translationX = 0F;
	protected float translationY = 0F;
	protected float rotationX = 0F;
	protected float rotationY = 0F;

	protected Vector3 dragDirection = Vector3.zero;
	
	protected RaycastHit hit;
	protected float zoomFactor;
	
	protected Vector3 v2 = Vector3.zero;
	protected Vector3 v3;
	protected Vector3 v4;
	
	Vector3 p1 = Vector3.zero;
	Vector3 p2 = Vector3.zero;
	
	private Vector3[] lines;
	private ArrayList linesArray;
	private MeshRenderer meshRenderer;
	
	private float invert = 1.0f;
	private float sensitivity = 3.0f;
	private float scrollSensitivity = 3.0f;
	
	Quaternion originalRotation;
	
	void Awake()
	{
		CreateLineMaterial();	
	}
	
	public void Start()
	{
		originalRotation = transform.localRotation;
		rotationY = 0;
		transform.localRotation = originalRotation * Quaternion.AngleAxis(rotationY, Vector3.left);
	}
	
	string[] transformTypeLables = new string[3] { "Move", "Rotate", "Scale" };
	public void OnGUI()
	{	
		//currTransformType = (TransformType)GUI.Toolbar( new Rect( 0,0,150,20), (int)currTransformType, transformTypeLables );	
	}
	
	public void Update()
	{

		if( Input.GetKey( KeyCode.E ) )
			currTransformType = TransformType.Rotate;
		if( Input.GetKey( KeyCode.F ) )
    		ResetCamera();
		
		UpdateHandleScale();			
		
		// Move object with handles
		if( Input.GetMouseButtonDown(0) )
		{
			if( SelectedObject != null && HandleClicked() )
			{
				// handle has be clicked, Begin draggin the object
				switch( currTransformType )
				{
				//case TransformType.Move: StartCoroutine( "DragObject" ); break;
				case TransformType.Rotate: StartCoroutine( "RotateObject" ); break;
				//case TransformType.Scale: StartCoroutine( "ScaleObject" ); break;
				}
			}
			else
			{	
				Ray ray = GetComponent<Camera>().ScreenPointToRay( Input.mousePosition );
                Collider[] gameObjects = GameObject.FindObjectsOfType(typeof(Collider)) as Collider[];
				float currDist = Mathf.Infinity;
				MeshFilter filter;
                RaycastHit hit;
                Physics.Raycast(ray, out hit);


                if(hit.collider != null)
                {
                    this.SelectObject(hit.collider.gameObject);

                }
                //foreach (Collider go in )
                //{
                /* filter = go.GetComponentInChildren(typeof(MeshFilter)) as MeshFilter;
                 if( filter != null )
                 {
                     Mesh m = filter.mesh;						
                     if( LineAABBIntersect(go.transform.InverseTransformPoint(ray.origin),go.transform.InverseTransformPoint(ray.GetPoint(5000)), m.bounds.min, m.bounds.max ) )
                     {
                         // we need to take the closest object if some objects overlap
                         float distToObject = Vector3.Distance(go.transform.position,transform.position);
                         if(  distToObject < currDist )
                         {
                             currDist = distToObject;

                         }// end if
                     }// end if	
                 }// end if
             }// end for*/
            }
        }// end if	
		
		// Zoom
		translationY = translationX = 0;
		float delta = Input.GetAxis ("Mouse ScrollWheel") * zoomFactor; 
		if( zoom && delta != 0 ) 
		{
			if( GetComponent<Camera>().rect.Contains(getMouseToScreen()) )
			{
				translationX = delta * scrollSensitivity;
				translationX *= Time.deltaTime;
				if( !GetComponent<Camera>().orthographic )
				{
					transform.Translate( translationY, 0, translationX );
				}
				else
				{
					//translationX *= camera.orthographicSize / 10.0f; // 10 % of zoom
					GetComponent<Camera>().orthographicSize	-= translationX;
					if( GetComponent<Camera>().orthographicSize < 1 ) GetComponent<Camera>().orthographicSize = 1;
					zoomFactor = GetComponent<Camera>().orthographicSize  * 100;
				}
			}// end if
		}// end if 
	}
	
	public void ResetCamera()
	{
		Vector3 newPos = SelectedTransform.position;
    	transform.position = new Vector3( newPos.x, newPos.y+1, newPos.z+5 );
    	transform.LookAt( newPos );
    		
		rotationY = 0;
		rotationX = 0;
		transform.localRotation = originalRotation * Quaternion.AngleAxis(rotationY, Vector3.left);
	}
	
	public void UpdateHandleScale()
	{
		if( SelectedTransform != null )
		{
			zoomFactor = Vector3.Distance( SelectedTransform.position, transform.position );
			Vector3 scale = SelectedTransform.localScale;
			xHandleBoxMin = new Vector3(0,-0.01f,-0.01f) * zoomFactor / scale.x;
			xHandleBoxMax = new Vector3(0.2f,0.02f,0.02f) * zoomFactor / scale.x;
			yHandleBoxMin = new Vector3(-0.01f,0,-0.01f) * zoomFactor / scale.y;
			yHandleBoxMax = new Vector3(0.02f,0.2f,0.02f) * zoomFactor / scale.y;
			zHandleBoxMin = new Vector3(-0.01f,-0.01f,0) * zoomFactor / scale.z;
			zHandleBoxMax = new Vector3(0.02f,0.02f,0.2f) * zoomFactor / scale.z;
		}
	}
	
	public void SelectObject( GameObject obj )
	{
		// set the object to be selected
		SelectedObject = obj;
		SelectedTransform = SelectedObject.transform;
		
		// save mesh info for rendering wireframe
		/*MeshFilter filter = SelectedObject.GetComponentInChildren<MeshFilter>();
		Mesh mesh = filter.mesh;
		Vector3[] vertices = mesh.vertices;
		int[] triangles = mesh.triangles;
	    lines = new Vector3[triangles.Length];
	    
		for( int i = 0; i < triangles.Length; i++ )
		{ 
			lines[i] = vertices[triangles[i]];
		}*/
	}

	public bool LineAABBIntersect( Vector3 p1, Vector3 p2, Vector3 min, Vector3 max )
	{
	    Vector3 d = (p2 - p1) * 0.5f;
	    Vector3 e = (max - min) * 0.5f;
	    Vector3 c = p1 + d - (min + max) * 0.5f;
	    Vector3 ad = new Vector3( Mathf.Abs(d.x), Mathf.Abs(d.y), Mathf.Abs(d.z) );
	
	    if (Mathf.Abs(c[0]) > e[0] + ad[0])
	        return false;
	    if (Mathf.Abs(c[1]) > e[1] + ad[1])
	        return false;
	    if (Mathf.Abs(c[2]) > e[2] + ad[2])
	        return false;
	  
	    if (Mathf.Abs(d[1] * c[2] - d[2] * c[1]) > e[1] * ad[2] + e[2] * ad[1] + Mathf.Epsilon)
	        return false;
	    if (Mathf.Abs(d[2] * c[0] - d[0] * c[2]) > e[2] * ad[0] + e[0] * ad[2] + Mathf.Epsilon)
	        return false;
	    if (Mathf.Abs(d[0] * c[1] - d[1] * c[0]) > e[0] * ad[1] + e[1] * ad[0] + Mathf.Epsilon)
	        return false;
	            
	    return true;
	}
	
	public float distance2Lines( Vector3 a, Vector3 b, Vector3 c, Vector3 d )
	{
		float dist = 0;
		
		Vector3 n = Vector3.Cross( (b - a), (c - d) );
		dist = Vector3.Dot( (d-a), n/n.magnitude);
		
		return Mathf.Abs(dist);
	}
	
	public bool HandleClicked()
	{	
		Ray ray = GetComponent<Camera>().ScreenPointToRay(Input.mousePosition);
		p1 = SelectedTransform.InverseTransformPoint( ray.origin );
		p2 = SelectedTransform.InverseTransformPoint( ray.GetPoint(5000) );

		/*if( LineAABBIntersect( p1 , p2, xHandleBoxMin, xHandleBoxMax) )
		{
			dragDirection = Vector3.right;
			HandleColorX = Color.yellow;
			HandleColorY = Color.green;
			HandleColorZ = Color.blue;
			return true;
		}*/
		
		// check the handle for the Y direction
		if( SelectedObject != null && SelectedObject.gameObject.GetComponent<SpiderLeg>() != null && LineAABBIntersect( p1 , p2, yHandleBoxMin, yHandleBoxMax) )
		{
			dragDirection = Vector3.up;
			HandleColorX = Color.red;
			HandleColorY = Color.yellow;
			HandleColorZ = Color.blue;
			return true;
		}
		
		// check the handle for the Z direction
		if(SelectedObject != null && SelectedObject.gameObject.GetComponent<SpiderLeg>() == null && LineAABBIntersect( p1 , p2, zHandleBoxMin, zHandleBoxMax) )
		{
			dragDirection = Vector3.forward;
			HandleColorX = Color.red;
			HandleColorY = Color.green;
			HandleColorZ = Color.yellow;
			return true;
		}
		
		return false;
	}
	
	
	
	public virtual IEnumerator RotateObject()
	{
		Ray ray = GetComponent<Camera>().ScreenPointToRay( Input.mousePosition );
		Transform trans = SelectedTransform;
		float distance = Vector3.Distance( SelectedTransform.position, transform.position );
		Vector3 initialMouse = ray.GetPoint(distance);
		Vector3 currMouse;

		while( Input.GetMouseButton(0) )
		{
			ray = GetComponent<Camera>().ScreenPointToRay( Input.mousePosition );
			currMouse = ray.GetPoint(distance);
			trans.Rotate( Vector3.Scale( trans.InverseTransformDirection(currMouse - initialMouse), dragDirection)*360, Space.Self );
			initialMouse = currMouse;
			yield return 0;
		}// end while
	}

	public Vector3 getMouseToScreen()
	{
		Vector3 mouse = Input.mousePosition;
		float x = mouse.x / Screen.width;
		float y = mouse.y / Screen.height;
		
		return new Vector3( x, y, 0 );
	}
	
	protected void CreateLineMaterial() 
	{ 
	    if( !lineMaterial ) 
	    { 
	        lineMaterial = new Material( "Shader \"Lines/Colored Blended\" {" +
	            "SubShader { Pass { " + 
	            "    BindChannels { Bind \"Color\",color } " + 
	            "    ZWrite Off Cull Off Fog { Mode Off } " + 
	            "} } }" ); 
	        lineMaterial.hideFlags = HideFlags.HideAndDontSave; 
	        lineMaterial.shader.hideFlags = HideFlags.HideAndDontSave; 
	    }
	    
	    if( !overlayMaterial ) 
	    { 
	        overlayMaterial = new Material( "Shader \"Lines/Colored Blended\" {" +
	            "SubShader { Pass { " + 
	            "    BindChannels { Bind \"Color\",color } " + 
	            "    ZTest Always ZWrite Off Cull Off Fog { Mode Off } " + 
	            "} } }" ); 
	        overlayMaterial.hideFlags = HideFlags.HideAndDontSave; 
	        overlayMaterial.shader.hideFlags = HideFlags.HideAndDontSave; 
	    }
	    
	    if( !gridMaterial ) 
	    { 
	    	gridMaterial = new Material(
        		"Shader \"Hidden/Invert\" {" +
        		"SubShader { Pass {" +
        		"    ZTest Always Cull Off ZWrite Off" +
        		"    SetTexture [_RenderTex] { combine one-texture }" +
        		"} } }" );
        	gridMaterial.hideFlags = HideFlags.HideAndDontSave; 
			gridMaterial.shader.hideFlags = HideFlags.HideAndDontSave;
	    }
	}
	
	protected void OnPreRender()
	{
		GL.Clear( true, true, new Color(0.19f,0.19f,0.19f,1.0f) );
		gridMaterial.SetPass( 0 );
		DrawGrid( 100, 100 );
	}

	protected void OnPostRender()
	{
		lineMaterial.SetPass( 0 );
		
		if( SelectedObject == null )
			return;
		
		GL.Color( colorLightBlue );
		//DrawWireFrameMesh();
		
		overlayMaterial.SetPass( 0 );
		
		GL.Color( colorLightGreen );
		DrawCollider();
		
		float dist = zoomFactor / 6;
		float rad;
		
		Vector3 v = SelectedTransform.position;
		
		v2 = SelectedTransform.TransformPoint(dist/SelectedTransform.localScale.x,0,0);
		v3 = SelectedTransform.TransformPoint(0,dist/SelectedTransform.localScale.y,0);
	    v4 = SelectedTransform.TransformPoint(0,0,dist/SelectedTransform.localScale.z);

	    GL.Begin( GL.LINES );

	    GL.Color( HandleColorX );
	    GL.Vertex( v );
	    GL.Vertex( v2 );
	    
	    GL.Color( HandleColorY );
	    GL.Vertex( v );
	    GL.Vertex( v3 );
	 
	    GL.Color( HandleColorZ );
	    GL.Vertex( v );
	    GL.Vertex( v4 );

	    GL.End();
   		
	    switch( currTransformType )
	    {
            case TransformType.Rotate:
	    	    rad = 0.125f * zoomFactor / 5;
	    	    //DrawCircleFillX( v2.x, v2.y, v2.z, rad, 0, HandleColorX );
                if(SelectedObject.GetComponent<SpiderLeg>() != null)
                {
                    DrawCircleFillY(v3.x, v3.y, v3.z, rad, 0, HandleColorY);
                }
                else
                {
                    DrawCircleFillZ(v4.x, v4.y, v4.z, rad, 0, HandleColorZ);
                }
	    	
	   		    
	   		    break;	   	
	    }// end if
	}
	
	/*protected void DrawWireFrameMesh()
	{
		GL.PushMatrix();
		GL.MultMatrix( SelectedTransform.localToWorldMatrix );
		
		GL.Begin( GL.LINES ); 
		 
		for( int i = 0; i < lines.Length / 3; i++ ) 
		{ 
		   GL.Vertex(lines[i * 3]); 
		   GL.Vertex(lines[i * 3 + 1]); 
		    
		   GL.Vertex(lines[i * 3 + 1]); 
		   GL.Vertex(lines[i * 3 + 2]); 
		    
		   GL.Vertex(lines[i * 3 + 2]); 
		   GL.Vertex(lines[i * 3]); 
		} 
		       
		GL.End(); 
		GL.PopMatrix(); 
	}*/
	
	protected void DrawCollider()
	{
		GL.PushMatrix();
		GL.MultMatrix( SelectedTransform.localToWorldMatrix );
		
		Collider col = SelectedObject.GetComponent<Collider>();
		if( col is BoxCollider )
		{
			BoxCollider box = col as BoxCollider;
			DrawBounds( box.center, box.size );
			
		}
		else if( col is CapsuleCollider )
		{
			CapsuleCollider capsule = col as CapsuleCollider;
			
		}
		else if( col is MeshCollider )
		{
			//DrawConvexMesh();
		}
		else if( col is SphereCollider )
		{
			SphereCollider sphere = col as SphereCollider;
			DrawCircleX( sphere.center.x, sphere.center.y, sphere.center.z, sphere.radius );
			DrawCircleY( sphere.center.x, sphere.center.y, sphere.center.z, sphere.radius );
			DrawCircleZ( sphere.center.x, sphere.center.y, sphere.center.z, sphere.radius );
		}
		else if( col is WheelCollider )
		{
			WheelCollider wheel = col as WheelCollider;
			DrawCircleY( wheel.center.x, wheel.center.y, wheel.center.z, wheel.radius );
			DrawRaycast( wheel.center, wheel.radius + wheel.suspensionDistance );
			
		}
		/*else if( col is RaycastCollider )
		{
			RaycastCollider raycast = col as RaycastCollider;
			DrawRaycast( raycast.center, raycast.length );			
		}*/
		
		GL.PopMatrix(); 
	}
	
	protected void DrawBounds( Vector3 center, Vector3 size )
	{
		Vector3 s = size / 2;
		DrawBox( center-s, center+s );
	}
	
	protected void DrawBox( Vector3 bmin, Vector3 bmax )
	{
		GL.Begin( GL.LINES );
		
		DrawLine( bmin, new Vector3(bmin.x, bmax.y, bmin.z) );
		DrawLine( bmin, new Vector3(bmin.x, bmin.y, bmax.z) );
		DrawLine( bmin, new Vector3(bmax.x, bmin.y, bmin.z) );
		
		DrawLine( new Vector3(bmin.x, bmax.y, bmax.z), new Vector3(bmax.x, bmax.y, bmax.z) );
		DrawLine( new Vector3(bmin.x, bmax.y, bmax.z), new Vector3(bmin.x, bmin.y, bmax.z) );
		DrawLine( new Vector3(bmin.x, bmax.y, bmax.z), new Vector3(bmin.x, bmax.y, bmin.z) );
		
		DrawLine( new Vector3(bmax.x, bmin.y, bmax.z), new Vector3(bmax.x, bmax.y, bmax.z) );
		DrawLine( new Vector3(bmax.x, bmin.y, bmax.z), new Vector3(bmax.x, bmin.y, bmin.z) );
		DrawLine( new Vector3(bmax.x, bmin.y, bmax.z), new Vector3(bmin.x, bmin.y, bmax.z) );
		
		DrawLine( new Vector3(bmax.x, bmax.y, bmin.z), new Vector3(bmin.x, bmax.y, bmin.z) );
		DrawLine( new Vector3(bmax.x, bmax.y, bmin.z), new Vector3(bmax.x, bmax.y, bmax.z) );
		DrawLine( new Vector3(bmax.x, bmax.y, bmin.z), new Vector3(bmax.x, bmin.y, bmin.z) );
		
		GL.End();	
	}
	
	protected void DrawRaycast( Vector3 center, float length )
	{
		Vector3 down = center;
		down.y -= length;
		GL.Begin( GL.LINES );
		DrawLine( center, down );
		GL.End();	
	}
	
	protected void DrawLine( Vector3 p1, Vector3 p2 )
	{
		GL.Vertex( p1 );
		GL.Vertex( p2 );
	}
	
	/*protected void DrawConvexMesh()
	{
		GL.PopMatrix();
		//DrawWireFrameMesh();
		GL.PushMatrix();
	}*/
	
	protected void DrawGrid( int rows, int columns )
	{
		// Render grid centered over (0,0)
		GL.Color( Color.grey );
		GL.Begin( GL.LINES );
	    for( int i=-rows; i<=rows; i++ )
	    {
	    	GL.Vertex3( -rows, 0, i );
	    	GL.Vertex3( columns, 0, i );
	    }
	    
	    for( int i=-columns; i<=columns; i++ )
	    {
	    	GL.Vertex3( i, 0, -columns );
	    	GL.Vertex3( i, 0, rows );
	    }
	 	GL.End();	
	}
	
	protected void DrawCircleFillX( float x, float y, float z, float radius, float depth, Color colour )
	{
		Transform trans = SelectedTransform;
		Vector3 p = trans.InverseTransformPoint( x, y, z );
		x = p.x * trans.localScale.x;
		y = p.y * trans.localScale.y;
		z = p.z * trans.localScale.z;
		
		GL.PushMatrix();
		Matrix4x4 rotationMatrix = Matrix4x4.TRS( trans.position, trans.rotation, Vector3.one );
		GL.MultMatrix( rotationMatrix );
		
		float y1 = p.y;
		float z1 = p.z;
		depth = depth/2;
		
		GL.Color( colour );
		GL.Begin( GL.TRIANGLES );
		
		for( int i=0; i<=360; i++ )
		{
			float angle=(float)(((float)i)/57.29577957795135);
			float z2 = p.z + (radius * Mathf.Sin(angle) );
			float y2 = p.y + (radius * Mathf.Cos(angle) );  
			GL.Vertex3( x+depth, y, z );
			GL.Vertex3( x-depth, y1, z1 );
			GL.Vertex3( x-depth, y2, z2 );
			y1 = y2;
			z1 = z2;
		}
		
		GL.End();
		GL.PopMatrix();
	}
	
	protected void DrawCircleFillY( float x, float y, float z, float radius, float depth, Color colour )
	{
		Transform trans = SelectedTransform;
		Vector3 p = trans.InverseTransformPoint( x, y, z );
		x = p.x * trans.localScale.x;
		y = p.y * trans.localScale.y;
		z = p.z * trans.localScale.z;
		
		GL.PushMatrix();
		Matrix4x4 rotationMatrix = Matrix4x4.TRS( trans.position, trans.rotation, Vector3.one );
		GL.MultMatrix( rotationMatrix );
		
		float z1 = p.z;
		float x1 = p.x;
		depth = depth/2;
		
		GL.Color( colour );
		GL.Begin( GL.TRIANGLES );
		
		for( int i=0; i<=360; i++ )
		{
			float angle=(float)(((float)i)/57.29577957795135);   
			float x2 = p.x + (radius * Mathf.Sin( angle) );
			float z2 = p.z + (radius * Mathf.Cos( angle) );             
			GL.Vertex3( x, y+depth, z );
			GL.Vertex3( x1, y-depth, z1 );
			GL.Vertex3( x2, y-depth, z2 );
			z1 = z2;
			x1 = x2;
		}
		
		GL.End();
		GL.PopMatrix();
	}

	protected void DrawCircleFillZ( float x, float y, float z, float radius, float depth, Color colour )
	{
		Transform trans = SelectedTransform;
		Vector3 p = trans.InverseTransformPoint( x, y, z );
		x = p.x * trans.localScale.x;
		y = p.y * trans.localScale.y;
		z = p.z * trans.localScale.z;
		
		GL.PushMatrix();
		Matrix4x4 rotationMatrix = Matrix4x4.TRS( trans.position, trans.rotation, Vector3.one );
		GL.MultMatrix( rotationMatrix );

		float y1 = p.y;
		float x1 = p.x;
		depth = depth/2;
		
		GL.Color( colour );
		GL.Begin( GL.TRIANGLES );
		
		for( int i=0; i<=360; i++ )
		{
			float angle=(float)(((float)i)/57.29577957795135);   
			float x2 = p.x + (radius * Mathf.Sin( angle) );
			float y2 = p.y + (radius * Mathf.Cos( angle) );             
			GL.Vertex3( x, y, z+depth );
			GL.Vertex3( x1, y1, z-depth );
			GL.Vertex3( x2, y2, z-depth );
			y1 = y2;
			x1 = x2;
		}
		
		GL.End();
		GL.PopMatrix();
	}
	
	protected void DrawCubeFill( float x, float y, float z, float size, Color colour )
	{
		Transform trans = SelectedTransform;
		Vector3 p = trans.InverseTransformPoint( x, y, z );
		x = p.x * trans.localScale.x;
		y = p.y * trans.localScale.y;
		z = p.z * trans.localScale.z;
		
		GL.PushMatrix();
		Matrix4x4 rotationMatrix = Matrix4x4.TRS( trans.position, trans.rotation, Vector3.one );
		GL.MultMatrix( rotationMatrix );
		
		float f = size/2;

		GL.Begin( GL.QUADS );			// Draw The Cube Using quads
	    GL.Color( colour);
	    GL.Vertex3( x+f, y+f, z-f );	// Top
	    GL.Vertex3( x-f, y+f, z-f );
	    GL.Vertex3( x-f, y+f, z+f );
	    GL.Vertex3( x+f, y+f, z+f );

	    GL.Vertex3( x+f, y-f, z+f );	// Bottom
	    GL.Vertex3( x-f, y-f, z+f );
	    GL.Vertex3( x-f, y-f, z-f );
	    GL.Vertex3( x+f, y-f, z-f );
	
	    GL.Vertex3( x+f, y+f, z+f );	// Front
	    GL.Vertex3( x-f, y+f, z+f );
	    GL.Vertex3( x-f, y-f, z+f );
	    GL.Vertex3( x+f, y-f, z+f );

	    GL.Vertex3( x+f, y-f, z-f );	// Back
	    GL.Vertex3( x-f, y-f, z-f );
	    GL.Vertex3( x-f, y+f, z-f );
	    GL.Vertex3( x+f, y+f, z-f );

	    GL.Vertex3( x-f, y+f, z+f );	// Left
	    GL.Vertex3( x-f, y+f, z-f );
	    GL.Vertex3( x-f, y-f, z-f );
	    GL.Vertex3( x-f, y-f, z+f );

	    GL.Vertex3( x+f, y+f, z-f );	// Right
	    GL.Vertex3( x+f, y+f, z+f );
	    GL.Vertex3( x+f, y-f, z+f );
	    GL.Vertex3( x+f, y-f, z-f );
		GL.End();
		
		GL.PopMatrix();
	}
 	
	protected void DrawCircleX( float x, float y, float z, float r ) 
	{
		float x1;
		float y1;

		GL.Begin( GL.LINES );
		
		for( int i = 0; i<180; i++ )
		{
			x1 = r * Mathf.Cos(i) - x;
			y1 = r * Mathf.Sin(i) + y;
			GL.Vertex3( x1 + y, y1 - x, z );
			x1 = r * Mathf.Cos(i + 0.1f) - x;
			y1 = r * Mathf.Sin(i + 0.1f) + y;
			GL.Vertex3( x1 + y, y1 - x, z );	
		}

		GL.End();
	}
	
	protected void DrawCircleY( float x, float y, float z, float r ) 
	{	
		float z1;
		float y1;

		GL.Begin( GL.LINES );
		
		for( int i = 0; i<180; i++ )
		{
			z1 = r * Mathf.Cos(i) - x;
			y1 = r * Mathf.Sin(i) + y;
			GL.Vertex3( x, y1 - x, z1 + y );
			z1 = r * Mathf.Cos(i + 0.1f) - x;
			y1 = r * Mathf.Sin(i + 0.1f) + y;
			GL.Vertex3( x, y1 - x, z1 + y );	
		}

		GL.End();
	}
	
	protected void DrawCircleZ( float x, float y, float z, float r ) 
	{
		float x1;
		float z1;

		GL.Begin( GL.LINES );
		
		for( int i = 0; i<180; i++ )
		{
			x1 = r * Mathf.Cos(i) - x;
			z1 = r * Mathf.Sin(i) + y;
			GL.Vertex3( x1 + y, y, z1 - x );
			x1 = r * Mathf.Cos(i + 0.1f) - x;
			z1 = r * Mathf.Sin(i + 0.1f) + y;
			GL.Vertex3( x1 + y, y, z1 - x );	
		}

		GL.End();
	}
}
