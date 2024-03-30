import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Function to load data from CSV file
def load_data(uploaded_file):
    try:
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            return data
        else:
            return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")
        return None


# Function to plot selected graph type
def plot_graph(data, selected_columns, graph_type):
    try:
        if graph_type == 'Histogram':
            for col in selected_columns:
                plt.figure()
                data[col].hist()
                plt.title(f'Histogram of {col}')
                plt.xlabel(col)
                plt.ylabel('Frequency')
                st.pyplot(plt)
        elif graph_type == 'Box Plot':
            plt.figure()
            data[selected_columns].boxplot()
            plt.title('Box Plot')
            plt.xlabel('Columns')
            plt.ylabel('Values')
            st.pyplot(plt)
        elif graph_type == 'Scatter Plot' and len(selected_columns) == 2:
            plt.figure()
            plt.scatter(data[selected_columns[0]], data[selected_columns[1]])
            plt.title(f'Scatter Plot of {selected_columns[0]} vs {selected_columns[1]}')
            plt.xlabel(selected_columns[0])
            plt.ylabel(selected_columns[1])
            st.pyplot(plt)
        else:
            st.error("Select exactly two columns for Scatter Plot.")
    except Exception as e:
        st.error(f"An error occurred while plotting the graph: {str(e)}")


# Function to display unique non-integer values for selected column
def display_unique_values(data, selected_column):
    if selected_column is not None:
        st.subheader(f"Unique Values for '{selected_column}'")
        non_integer_values = data[selected_column][~data[selected_column].apply(str).str.isnumeric()]
        unique_values = non_integer_values.unique()
        st.table(pd.DataFrame(unique_values, columns=[selected_column]))


# Function to display filtered data based on selected columns and values
def display_filtered_data(data, selected_columns, selected_values):
    if selected_columns and selected_values:
        filtered_data = data[data[selected_columns[0]].isin(selected_values[0])]
        for col, values in zip(selected_columns[1:], selected_values[1:]):
            filtered_data = filtered_data[filtered_data[col].isin(values)]
        st.subheader("Filtered Data")
        st.write(filtered_data)


# Function to display correlation matrix as heatmap
def display_correlation_matrix(data):
    try:
        st.subheader("Correlation Matrix Heatmap")
        corr_matrix = data.corr()
        plt.figure(figsize=(10, 8))
        plt.imshow(corr_matrix, cmap='viridis', interpolation='nearest')
        plt.colorbar(label='Correlation')
        plt.xticks(range(len(data.columns)), data.columns, rotation=45)
        plt.yticks(range(len(data.columns)), data.columns)
        plt.title("Correlation Matrix Heatmap")
        st.pyplot(plt)
    except Exception as e:
        st.error(f"An error occurred while displaying correlation matrix heatmap: {str(e)}")


# Main app function
def main():
    st.title("Data Analysis Tool")

    uploaded_file = st.file_uploader("Upload CSV File", type='csv')
    if uploaded_file is not None:
        data = load_data(uploaded_file)

        if data is not None:
            st.write("Data Overview:", data.head())

            selected_columns = st.multiselect('Select Columns', data.columns)
            graph_type = st.selectbox('Select Graph Type', ['Histogram', 'Box Plot', 'Scatter Plot'])

            if st.button("Generate Plot"):
                plot_graph(data, selected_columns, graph_type)

            st.sidebar.title("Filter Data")
            for col in data.columns:
                if data[col].dtype in ['int64', 'float64']:
                    filter_type = st.sidebar.radio(f"Filter by {col}", options=['Constant Value', 'Range'])
                    if filter_type == 'Constant Value':
                        constant_value = st.sidebar.number_input(f"Enter constant value for {col}", value=0.0, step=1.0,
                                                                 key=f"{col}_const")
                        apply_button_key = f"apply_button_{col}_const"
                        if st.sidebar.button("Apply Filter", key=apply_button_key):
                            display_filtered_data(data, [col], [[constant_value]])
                    elif filter_type == 'Range':
                        range_start = st.sidebar.number_input(f"Enter start value for {col}", value=0.0, step=1.0,
                                                              key=f"{col}_start")
                        range_end = st.sidebar.number_input(f"Enter end value for {col}", value=100.0, step=1.0,
                                                            key=f"{col}_end")
                        apply_button_key = f"apply_button_{col}_range"
                        if st.sidebar.button("Apply Filter", key=apply_button_key):
                            filtered_data = data[(data[col] >= range_start) & (data[col] <= range_end)]
                            display_filtered_data(filtered_data, [], [])
                else:
                    multiselect_key = f"multiselect_{col}"
                    selected_columns_filter = st.sidebar.multiselect(f"Select values for {col}",
                                                                     options=data[col].unique(), key=multiselect_key)
                    if selected_columns_filter:
                        display_filtered_data(data, [col], [selected_columns_filter])

            st.sidebar.title("Unique Non-Integer Values")
            selected_column = st.sidebar.selectbox("Select Column", options=[''] + list(data.columns))
            display_unique_values(data, selected_column)

            display_correlation_matrix(data)


if __name__ == '__main__':
    main()
