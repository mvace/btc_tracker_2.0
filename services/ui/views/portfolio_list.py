def portfolio_list_view():
    """Display the list of all portfolios."""

    portfolio_response = requests.get(
        f"{API_URL}/portfolio/",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )

    if portfolio_response.status_code == 200:
        portfolios = portfolio_response.json()
        st.header(f"You have {len(portfolios)} portfolios.")
        if not portfolios:
            st.info("You have no portfolios yet. Create one using the form below.")
        else:
            for portfolio in portfolios:
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    st.write(f"**Portfolio ID:** {portfolio['id']}")
                with col2:
                    st.write(f"**Name:** {portfolio['name']}")
                with col3:
                    # CHANGE #1: Use st.button instead of st.link_button
                    # A unique key is crucial for buttons inside a loop.
                    if st.button("View Details", key=f"view_{portfolio['id']}"):
                        # Set the query parameter to the portfolio id
                        st.query_params["portfolio_id"] = portfolio["id"]
                        st.rerun()
                st.divider()
    elif portfolio_response.status_code == 401:
        auth.logout_user(cookies=cookies)
        st.rerun()
    else:
        st.error("Failed to retrieve portfolios.")
