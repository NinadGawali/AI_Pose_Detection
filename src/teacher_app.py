"""
Teacher Dashboard
View all students' statistics and performance
"""

import streamlit as st
import pandas as pd
from data_manager import DataManager
import plotly.express as px
import plotly.graph_objects as go


def show_teacher_dashboard(username, full_name):
    """Display teacher dashboard with student analytics"""
    
    st.markdown("""
    <style>
        .teacher-header {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 35px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        
        .teacher-title {
            font-size: 46px;
            font-weight: 700;
            color: white;
            margin-bottom: 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        .teacher-subtitle {
            font-size: 22px;
            color: #fff5f7;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        
        .metric-value {
            font-size: 44px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .metric-label {
            font-size: 17px;
            opacity: 0.95;
        }
        
        .student-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.12);
            margin: 10px 0;
            border-left: 5px solid #667eea;
        }
        
        .student-name {
            font-size: 21px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 10px;
        }
        
        .student-stat {
            font-size: 15px;
            color: #6b7280;
            margin: 5px 0;
        }
        
        .pose-stat-box {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 22px;
            border-radius: 12px;
            margin: 10px 0;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .activity-item {
            background: rgba(249, 250, 251, 0.95);
            padding: 18px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 5px solid #3b82f6;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            font-size: 16px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="teacher-header">
        <div class="teacher-title">👨‍🏫 Teacher Analytics Portal</div>
        <div class="teacher-subtitle">Welcome, {full_name}!</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 All Students", "🔍 Individual Student", "📈 Pose Analytics"])
    
    with tab1:
        show_overview()
    
    with tab2:
        show_all_students()
    
    with tab3:
        show_individual_student()
    
    with tab4:
        show_pose_analytics()


def show_overview():
    """Show overall statistics dashboard"""
    
    data_manager = DataManager()
    students_summary = data_manager.get_all_students_summary()
    recent_activities = data_manager.get_recent_activities(limit=15)
    
    if not students_summary:
        st.info("📚 No student data available yet. Students need to start practicing.")
        return
    
    # Calculate overall metrics
    total_students = len(students_summary)
    total_sessions = sum([s['Total_Sessions'] for s in students_summary])
    avg_overall_accuracy = sum([s['Avg_Accuracy'] for s in students_summary]) / total_students if total_students > 0 else 0
    
    # Top performer
    top_student = max(students_summary, key=lambda x: x['Avg_Accuracy'])
    
    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_students}</div>
            <div class='metric-label'>Total Students</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_sessions}</div>
            <div class='metric-label'>Total Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{round(avg_overall_accuracy, 1)}%</div>
            <div class='metric-label'>Average Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div class='metric-value'>🏆</div>
            <div class='metric-label'>Top: {top_student['Student_Name']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activities
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🕐 Recent Activities")
        if recent_activities:
            for activity in recent_activities[:10]:
                accuracy_color = get_accuracy_color(activity['Accuracy'])
                st.markdown(f"""
                <div class='activity-item' style='border-left-color: {accuracy_color};'>
                    <strong>{activity['Student_Name']}</strong> practiced <strong>{activity['Pose_Type']}</strong><br>
                    <span style='color: #6b7280; font-size: 13px;'>
                        📅 {activity['Date']} at {activity['Time']} | 
                        Accuracy: <span style='color: {accuracy_color}; font-weight: 600;'>{activity['Accuracy']}%</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activities.")
    
    with col2:
        st.markdown("### 📊 Student Performance")
        
        # Create performance distribution chart
        df = pd.DataFrame(students_summary)
        
        fig = go.Figure(data=[
            go.Bar(
                x=df['Student_Name'],
                y=df['Avg_Accuracy'],
                marker_color=df['Avg_Accuracy'].apply(lambda x: get_accuracy_color(x)),
                text=df['Avg_Accuracy'].round(1),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Average Accuracy by Student",
            xaxis_title="Student",
            yaxis_title="Accuracy (%)",
            yaxis_range=[0, 100],
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_all_students():
    """Show all students summary"""
    
    data_manager = DataManager()
    students_summary = data_manager.get_all_students_summary()
    
    if not students_summary:
        st.info("📚 No student data available yet.")
        return
    
    st.markdown("### 👥 All Students Performance Summary")
    
    # Convert to DataFrame for display
    df = pd.DataFrame(students_summary)
    df = df[[
        'Student_Name', 'Student_ID', 'Total_Sessions', 
        'Avg_Accuracy', 'Max_Accuracy', 'Min_Accuracy', 'Last_Practice'
    ]]
    df.columns = [
        'Student Name', 'Student ID', 'Total Sessions',
        'Avg Accuracy (%)', 'Best (%)', 'Lowest (%)', 'Last Practice'
    ]
    
    # Sort by average accuracy
    df = df.sort_values('Avg Accuracy (%)', ascending=False)
    
    # Style the dataframe
    st.dataframe(
        df.style.background_gradient(subset=['Avg Accuracy (%)'], cmap='RdYlGn', vmin=0, vmax=100),
        use_container_width=True,
        hide_index=True
    )
    
    # Performance distribution
    st.markdown("---")
    st.markdown("### 📈 Performance Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sessions per student
        fig1 = px.pie(
            df,
            values='Total Sessions',
            names='Student Name',
            title='Sessions Distribution',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Accuracy comparison
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=df['Student Name'],
            y=df['Avg Accuracy (%)'],
            mode='lines+markers',
            name='Average',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10)
        ))
        
        fig2.add_trace(go.Scatter(
            x=df['Student Name'],
            y=df['Best (%)'],
            mode='markers',
            name='Best',
            marker=dict(color='#22c55e', size=8, symbol='star')
        ))
        
        fig2.update_layout(
            title='Accuracy Trends',
            yaxis_title='Accuracy (%)',
            yaxis_range=[0, 100],
            showlegend=True
        )
        
        st.plotly_chart(fig2, use_container_width=True)


def show_individual_student():
    """Show detailed statistics for a specific student"""
    
    data_manager = DataManager()
    students_summary = data_manager.get_all_students_summary()
    
    if not students_summary:
        st.info("📚 No student data available yet.")
        return
    
    st.markdown("### 🔍 Select a Student for Detailed Analysis")
    
    # Student selection
    student_options = {s['Student_Name']: s['Student_ID'] for s in students_summary}
    selected_student_name = st.selectbox("Choose Student", list(student_options.keys()))
    selected_student_id = student_options[selected_student_name]
    
    # Get detailed stats
    stats = data_manager.get_student_stats(selected_student_id)
    
    if not stats:
        st.warning("No data available for this student.")
        return
    
    # Student summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div class='metric-value'>{stats['total_sessions']}</div>
            <div class='metric-label'>Total Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
            <div class='metric-value'>{stats['avg_accuracy']}%</div>
            <div class='metric-label'>Average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);'>
            <div class='metric-value'>{stats['max_accuracy']}%</div>
            <div class='metric-label'>Best Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
            <div class='metric-value'>{stats['min_accuracy']}%</div>
            <div class='metric-label'>Lowest Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent sessions
    st.markdown(f"### 📅 {selected_student_name}'s Recent Sessions")
    
    if stats['recent_sessions']:
        df = pd.DataFrame(stats['recent_sessions'])
        df = df[['Date', 'Time', 'Pose_Type', 'Accuracy', 'Duration_Seconds']]
        df.columns = ['Date', 'Time', 'Pose', 'Accuracy (%)', 'Duration (s)']
        
        st.dataframe(
            df.style.background_gradient(subset=['Accuracy (%)'], cmap='RdYlGn', vmin=0, vmax=100),
            use_container_width=True,
            hide_index=True
        )
        
        # Progress chart
        st.markdown("### 📈 Progress Over Time")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(len(df))),
            y=df['Accuracy (%)'],
            mode='lines+markers',
            name='Accuracy',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10, color=df['Accuracy (%)'], 
                       colorscale='RdYlGn', showscale=True,
                       cmin=0, cmax=100)
        ))
        
        fig.update_layout(
            xaxis_title='Session Number',
            yaxis_title='Accuracy (%)',
            yaxis_range=[0, 100],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sessions recorded yet.")


def show_pose_analytics():
    """Show analytics by pose type"""
    
    data_manager = DataManager()
    pose_stats = data_manager.get_pose_statistics()
    
    if not pose_stats:
        st.info("📚 No pose data available yet.")
        return
    
    st.markdown("### 📊 Performance by Pose Type")
    
    # Convert to DataFrame
    df = pd.DataFrame(pose_stats).T
    df = df.reset_index()
    df.columns = ['Pose', 'Average (%)', 'Total Sessions', 'Best (%)', 'Worst (%)']
    
    # Display table
    st.dataframe(
        df.style.background_gradient(subset=['Average (%)'], cmap='RdYlGn', vmin=0, vmax=100),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Average Accuracy by Pose")
        
        fig1 = go.Figure(data=[
            go.Bar(
                x=df['Pose'],
                y=df['Average (%)'],
                marker_color=df['Average (%)'].apply(lambda x: get_accuracy_color(x)),
                text=df['Average (%)'].round(1),
                textposition='auto',
            )
        ])
        
        fig1.update_layout(
            yaxis_title='Average Accuracy (%)',
            yaxis_range=[0, 100],
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Session Count by Pose")
        
        fig2 = px.pie(
            df,
            values='Total Sessions',
            names='Pose',
            title='Practice Session Distribution',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Difficulty analysis
    st.markdown("---")
    st.markdown("### 🎯 Pose Difficulty Analysis")
    
    df_sorted = df.sort_values('Average (%)')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔴 Most Challenging")
        if len(df_sorted) > 0:
            hardest = df_sorted.iloc[0]
            st.markdown(f"""
            <div class='pose-stat-box' style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);'>
                <h3>{hardest['Pose']}</h3>
                <p style='font-size: 24px; font-weight: 700;'>{hardest['Average (%)']}% avg</p>
                <p style='font-size: 14px;'>{int(hardest['Total Sessions'])} sessions</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🟡 Medium Difficulty")
        if len(df_sorted) > 1:
            mid_idx = len(df_sorted) // 2
            medium = df_sorted.iloc[mid_idx]
            st.markdown(f"""
            <div class='pose-stat-box' style='background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);'>
                <h3>{medium['Pose']}</h3>
                <p style='font-size: 24px; font-weight: 700;'>{medium['Average (%)']}% avg</p>
                <p style='font-size: 14px;'>{int(medium['Total Sessions'])} sessions</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 🟢 Easiest")
        if len(df_sorted) > 0:
            easiest = df_sorted.iloc[-1]
            st.markdown(f"""
            <div class='pose-stat-box' style='background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%);'>
                <h3>{easiest['Pose']}</h3>
                <p style='font-size: 24px; font-weight: 700;'>{easiest['Average (%)']}% avg</p>
                <p style='font-size: 14px;'>{int(easiest['Total Sessions'])} sessions</p>
            </div>
            """, unsafe_allow_html=True)


def get_accuracy_color(accuracy):
    """Get color based on accuracy value"""
    if accuracy >= 85:
        return "#22c55e"
    elif accuracy >= 70:
        return "#3b82f6"
    elif accuracy >= 50:
        return "#f59e0b"
    else:
        return "#ef4444"
