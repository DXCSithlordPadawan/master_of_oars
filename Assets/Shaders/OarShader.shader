Shader "Custom/NavalOars"
{
    Properties {
        _MainTex ("Texture", 2D) = "white" {}
        _RowSpeed ("Rowing Speed", Float) = 1.0
        _Amplitude ("Stroke Depth", Float) = 0.5
    }
    SubShader {
        Tags { "RenderType"="Opaque" }
        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            float _RowSpeed;
            float _Amplitude;

            v2f vert (appdata v) {
                v2f o;
                // Create sine-wave motion for oar oscillation
                float wave = sin(_Time.y * _RowSpeed * 5.0) * _Amplitude;
                v.vertex.x += wave * (v.vertex.y); // Pivot based on height
                
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target {
                return tex2D(_MainTex, i.uv);
            }
            ENDCG
        }
    }
}