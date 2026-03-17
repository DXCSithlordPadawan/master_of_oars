Shader "Custom/NavalWake"
{
    Properties {
        _MainTex ("Wake Texture", 2D) = "white" {}
        _FlowSpeed ("Flow Speed", Float) = 2.0
        _Transparency ("Global Opacity", Range(0,1)) = 0.5
    }
    SubShader {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off

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

            float _FlowSpeed;
            float _Transparency;
            sampler2D _MainTex;

            v2f vert (appdata v) {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                // Scroll UVs backward to simulate forward movement
                o.uv = v.uv + float2(0, _Time.y * _FlowSpeed);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target {
                fixed4 col = tex2D(_MainTex, i.uv);
                col.a *= _Transparency;
                return col;
            }
            ENDCG
        }
    }
}