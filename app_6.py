import streamlit as st
import pandas as pd
import pulp
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ShiftScheduler import ShiftScheduler

# タイトル
st.title("シフトスケジューリングアプリ")

# サイドバー
st.sidebar.header("データのアップロード")
# csvファイルのアップロード
calendar_file = st.sidebar.file_uploader("カレンダー", type=["csv"])
staff_file = st.sidebar.file_uploader("スタッフ", type=["csv"])

# タブ
tab1, tab2, tab3 = st.tabs(["カレンダー情報", "スタッフ情報", "シフト表作成"])

with tab1:
    # csv入力データを表として可視化する
    if calendar_file is None:
        st.write("カレンダー情報をアップロードしてください")
    else:
        # アップロードされたファイルをデータフレームに読み込む
        st.markdown("## カレンダー情報")
        calendar_df = pd.read_csv(calendar_file)
        st.table(calendar_df)
        
with tab2:
    # csv入力データを表として可視化する
    if staff_file is None:
        st.write("スタッフ情報をアップロードしてください")
    else:
        # アップロードされたファイルをデータフレームに読み込む
        st.markdown("## スタッフ情報")
        staff_df = pd.read_csv(staff_file)
        st.table(staff_df)

with tab3:
    # st.markdown("## 最適化結果")
    # st.markdown("## シフト表")
    if staff_file is None:
        st.write("スタッフ情報をアップロードしてください")
    if calendar_file is None:
        st.write("カレンダー情報をアップロードしてください")
    if staff_file is not None and calendar_file is not None:
        if st.button('最適化実行'):
            st.markdown("## 最適化結果")
            
            ss = ShiftScheduler()
            ss.set_data(staff_df, calendar_df)
            ss.build_model()
            ss.solve()

            # 最適化結果の出力
            st.write("実行ステータス:", pulp.LpStatus[ss.status])
            st.write("目的関数値:", pulp.value(ss.model.objective))

            st.markdown("## シフト表")
            st.table(ss.sch_df)
            
            st.markdown("## スタッフの希望の確認")
            shift_sum = ss.sch_df.sum(axis=1)
            st.bar_chart(shift_sum)

            st.markdown("## シフト数の充足確認")
            # 各スロットの合計シフト数をstreamlitのbar chartで表示
            shift_sum_slot = ss.sch_df.sum(axis=0)
            st.bar_chart(shift_sum_slot)

            st.markdown("## 責任者の合計シフト数の充足確認")
            # shift_scheduleに対してstaff_dataをマージして責任者の合計シフト数を計算
            shift_schedule_with_staff_data = pd.merge(
                ss.sch_df,
                staff_df,
                left_index=True,
                right_on="スタッフID",
            )
            # 責任者フラグが1の行のみqueryで抽出
            shift_chief_only = shift_schedule_with_staff_data.query("責任者フラグ == 1")
            # 不要な列はdropで削除する
            shift_chief_only = shift_chief_only.drop(
                columns=[
                    "スタッフID",
                    "責任者フラグ",
                    "希望最小出勤日数",
                    "希望最大出勤日数",
                ]
            )
            shift_chief_sum = shift_chief_only.sum(axis=0)
            st.bar_chart(shift_chief_sum)

            st.download_button(
                label="シフト表をダウンロード",
                data=ss.sch_df.to_csv().encode("utf-8"),
                file_name="output.csv",
                mime="text/csv",
            )
            
            
        
    # st.markdown("## シフト数の充足確認")
    # st.markdown("## スタッフの希望の確認")
    # st.markdown("## 責任者の合計シフト数の充足確認")
